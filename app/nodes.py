import sys
import io
import unittest
from app.state import AgentState
from app.chains import generate_chain, reflect_chain, test_chain

# --- Node 1: Write Tests (NEW) ---
def test_generation_node(state: AgentState):
    print("--- GENERATING TESTS ---")
    response = test_chain.invoke({"requirement": state["requirement"]})
    cleaned_tests = response.content.replace("```python", "").replace("```", "").strip()
    return {"test_code": cleaned_tests}

# --- Node 2: Write Code ---
def generation_node(state: AgentState):
    print("--- GENERATING SOLUTION ---")
    response = generate_chain.invoke({
        "requirement": state["requirement"],
        "test_code": state["test_code"], # Pass tests so it knows what to satisfy
        "code": state.get("code", ""),
        "error": state.get("error", ""),
        "reflection": state.get("reflection", "")
    })
    cleaned_code = response.content.replace("```python", "").replace("```", "").strip()
    
    return {
        "code": cleaned_code,
        "iterations": state.get("iterations", 0) + 1,
        "error": None
    }

# --- Node 3: Execute (Complex) ---
def execution_node(state: AgentState):
    print("--- EXECUTING TESTS ---")
    
    # We need to run the Tests AGAINST the Solution.
    # We will combine them into one temporary script for execution.
    
    # 1. Define the code as a module string
    solution_code = state["code"]
    test_code = state["test_code"]
    
    # Hack: We mock the 'solution' module so the test can import it
    full_script = f"""
import sys
from types import ModuleType

# Create a fake module named 'solution'
sol = ModuleType('solution')
sys.modules['solution'] = sol

# Execute the solution code inside that module
exec('''{solution_code}''', sol.__dict__)

# Now run the tests
{test_code}

if __name__ == '__main__':
    unittest.main(exit=False)
"""
    
    # Capture Output
    old_stderr = sys.stderr
    sys.stderr = io.StringIO() # Unittest prints to stderr
    
    try:
        # EXECUTE EVERYTHING
        exec(full_script, {'__name__': '__main__'})
        output_log = sys.stderr.getvalue()
        
        # Check if tests failed (look for "FAILED" in output)
        if "FAILED" in output_log or "Error" in output_log:
            return {"output": output_log, "error": output_log} # Treat test failure as an error
        else:
            return {"output": output_log, "error": None}
            
    except Exception as e:
        return {"output": None, "error": str(e)}
        
    finally:
        sys.stderr = old_stderr

# --- Node 4: Reflect ---
def reflection_node(state: AgentState):
    print("--- REFLECTING ---")
    response = reflect_chain.invoke({
        "requirement": state["requirement"],
        "code": state["code"],
        "error": state["error"]
    })
    return {"reflection": response.content}
import sys
import io
import unittest
from app.state import AgentState
from app.chains import generate_chain, reflect_chain, test_chain

# --- Node 1: Write Tests ---
def test_generation_node(state: AgentState):
    print("--- GENERATING TESTS ---")
    response = test_chain.invoke({"requirement": state["requirement"]})
    cleaned_tests = response.content.replace("```python", "").replace("```", "").strip()
    return {"test_code": cleaned_tests}

# --- Node 2: Write Solution ---
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

# --- Node 3: Execute (Run Tests vs Solution) ---
def execution_node(state: AgentState):
    print("--- EXECUTING TESTS ---")
    
    solution_code = state["code"]
    test_code = state["test_code"]
    
    # Python Hack: Dynamically create a module named 'solution'
    full_script = f"""
import sys
from types import ModuleType

# 1. Create fake module
sol = ModuleType('solution')
sys.modules['solution'] = sol

# 2. Load the solution code into that module
exec('''{solution_code}''', sol.__dict__)

# 3. Run the unit tests
{test_code}

# 4. Safety net for unittest
if __name__ == '__main__':
    import unittest
    try:
        unittest.main(exit=False)
    except:
        pass
"""
    
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    try:
        # EXECUTE
        exec(full_script, {'__name__': '__main__'})
        output_log = sys.stderr.getvalue()
        
        if "FAILED" in output_log or "Error" in output_log:
            return {"output": output_log, "error": output_log}
        else:
            return {"output": output_log, "error": None}
            
    except SystemExit:
        # CRITICAL FIX: Catch the "Exit" command from unittest so the app stays alive!
        output_log = sys.stderr.getvalue()
        if "FAILED" in output_log or "Error" in output_log:
            return {"output": output_log, "error": output_log}
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
import sys
import io
import unittest
from types import ModuleType
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
        "test_code": state["test_code"],
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

# --- Node 3: Execute (The Fix: Manual Test Loader) ---
def execution_node(state: AgentState):
    print("--- EXECUTING TESTS ---")
    
    solution_code = state["code"]
    test_code = state["test_code"]
    
    # We explicitly find the test class and run it, instead of relying on unittest.main()
    full_script = f"""
import sys
import unittest
from types import ModuleType

# 1. Create fake module for the solution
sol = ModuleType('solution')
sys.modules['solution'] = sol
exec('''{solution_code}''', sol.__dict__)

# 2. Load the tests definition
{test_code}

# 3. FORCE RUN
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Find the Test Class dynamically (Look for any class inheriting from TestCase)
    test_cases = [obj for name, obj in locals().items() 
                  if isinstance(obj, type) and issubclass(obj, unittest.TestCase)]
    
    for test_class in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run with a text runner so we capture the output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        print("FAILED")
        # We do NOT exit here, we just print FAILED so the node catches it.
"""
    
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    try:
        # Execute the script that runs the tests
        exec(full_script, {'__name__': '__main__'})
        output_log = sys.stderr.getvalue()
        
        # Double check if it actually ran tests
        if "Ran 0 tests" in output_log or "NO TESTS RAN" in output_log:
             return {"output": output_log, "error": "No tests were found to run! (Check naming convention)"}

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
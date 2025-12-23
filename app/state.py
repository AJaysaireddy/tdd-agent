from typing import TypedDict, Optional

class AgentState(TypedDict):
    requirement: str        # User request
    test_code: str          # The Unit Tests (NEW)
    code: str               # The Solution Code
    output: Optional[str]   # Console output
    error: Optional[str]    # Error message
    reflection: Optional[str] 
    iterations: int
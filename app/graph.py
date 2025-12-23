from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.nodes import test_generation_node, generation_node, execution_node, reflection_node

# Logic
def should_continue(state: AgentState):
    if state["iterations"] > 3:
        return END
    if not state["error"]:
        return END
    return "reflect"

# Build Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("write_tests", test_generation_node) # NEW
workflow.add_node("generate", generation_node)
workflow.add_node("execute", execution_node)
workflow.add_node("reflect", reflection_node)

# Flow
workflow.set_entry_point("write_tests") # Start by writing tests!
workflow.add_edge("write_tests", "generate")
workflow.add_edge("generate", "execute")

workflow.add_conditional_edges(
    "execute", 
    should_continue, 
    {END: END, "reflect": "reflect"}
)

workflow.add_edge("reflect", "generate")

app_graph = workflow.compile()
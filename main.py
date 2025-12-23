import streamlit as st
from app.graph import app_graph

st.set_page_config(page_title="TDD Reflexion Agent", layout="wide")

st.title("🧪 TDD Self-Healing Agent")
st.markdown("I write a **Unit Test** first, then write code to pass it. If I fail, I fix myself.")

# Input
requirement = st.text_area("Requirement:", height=100, placeholder="e.g., Create a function add(a,b) that handles string inputs by converting them to int.")

if st.button("Build & Test"):
    if not requirement:
        st.error("Enter a requirement")
    else:
        status = st.container()
        
        # Initial State
        state = {
            "requirement": requirement, 
            "iterations": 0, 
            "test_code": "",
            "code": "", 
            "error": None,
            "output": None,
            "reflection": ""
        }
        
        with status:
            for event in app_graph.stream(state):
                for key, value in event.items():
                    state.update(value)
                    
                    if key == "write_tests":
                        st.info("📝 **Drafted Unit Tests**")
                        with st.expander("View Test Code"):
                            st.code(state["test_code"], language="python")
                            
                    elif key == "generate":
                        st.info(f"🔨 **Drafted Solution** (Attempt {state['iterations']})")
                        with st.expander("View Solution Code"):
                            st.code(state["code"], language="python")
                    
                    elif key == "execute":
                        if state["error"]:
                            st.error(f"❌ **Tests Failed**")
                            with st.expander("View Error Log"):
                                st.code(state["error"])
                        else:
                            st.success("✅ **Tests Passed!**")
                            st.text(state["output"])
                    
                    elif key == "reflect":
                        st.warning(f"🤔 **Reflecting...**")
                        st.write(f"Insight: {state['reflection']}")

        if state["code"] and not state["error"]:
            st.balloons()
            st.header("🚀 Final Verified Code")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("The Solution")
                st.code(state["code"], language="python")
            with col2:
                st.subheader("The Tests")
                st.code(state["test_code"], language="python")
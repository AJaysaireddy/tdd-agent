import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)

# --- PROMPT 1: The Tester (NEW) ---
test_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a QA Engineer. Write a Python script using 'unittest' to verify the user's requirement.\n"
        "The test should import the function from a module named 'solution'.\n"
        "Output ONLY the test code."
    )),
    ("user", "Requirement: {requirement}")
])

# --- PROMPT 2: The Coder (Updated) ---
gen_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Python Developer. Write a script that solves the requirement.\n"
        "Output ONLY valid Python code."
    )),
    ("user", (
        "Requirement: {requirement}\n"
        "Test Cases that must pass:\n{test_code}\n"
        "Previous Code: {code}\n"
        "Error to fix: {error}\n"
        "Reflection: {reflection}"
    ))
])

# --- PROMPT 3: The Debugger ---
reflect_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a debugger. Analyze the error trace and explain the fix."),
    ("user", "Requirement: {requirement}\nCode: {code}\nError: {error}")
])

# Connect Chains
test_chain = test_prompt | llm  # NEW
generate_chain = gen_prompt | llm
reflect_chain = reflect_prompt | llm
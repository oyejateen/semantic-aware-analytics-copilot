import streamlit as st
import langchain as lc

st.set_page_config(page_title="RAG Data Copilot", page_icon="💬")

st.title("Kona (코나 / कोना)")
st.write("your semantic aware RAG data copilot")

st.write(f"LangChain version: {lc.__version__}")

query = st.text_input("Enter a question")

if query:
    st.info(f"You entered: {query}")

import streamlit as st

st.title("ML Service Running on Render 🚀")

st.write("This is a basic ML app placeholder.")

# Simple input
number = st.number_input("Enter a number:")

# Simple output
if st.button("Process"):
    result = number * 2
    st.success(f"Result: {result}")

import streamlit as st
import numpy as np
import pandas as pd
import time

st.title("🎈 Streamlit Test App")

st.header("Testing Visual Connection")

st.write("If you can see this page, your Streamlit connection is working!")

# Interactive widgets
name = st.text_input("Enter your name:", "User")
st.write(f"Hello, {name}! 👋")

# Slider
age = st.slider("Select a number:", 0, 100, 25)
st.write(f"Selected value: {age}")

# Chart
st.subheader("Sample Chart")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)
st.line_chart(chart_data)

# Buttons
if st.button("Click me!"):
    st.balloons()
    st.success("Button clicked! 🎉")

# Sidebar
with st.sidebar:
    st.header("Sidebar")
    st.write("This is the sidebar")
    option = st.selectbox(
        "Choose an option:",
        ["Option 1", "Option 2", "Option 3"]
    )
    st.write(f"You selected: {option}")

st.info("💡 To access this from your local browser, use SSH port forwarding:\n\n`ssh -L 8501:localhost:8501 your_username@cluster_address`")

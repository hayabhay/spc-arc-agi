import streamlit as st
from config import DEV, get_page_config, init_session

# Set up page config & init session
st.set_page_config(**get_page_config())
init_session(st.session_state)

# Render session state if in dev mode
if DEV:
    with st.sidebar.expander("Session state"):
        st.write(st.session_state)

# Aliases for readability
# --------------------------------
st.write("### 🏠 Home")
st.write("---")

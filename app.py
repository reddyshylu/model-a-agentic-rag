"""Model A (Streamlit). Run:  python -m streamlit run app.py
DEMO ONLY: the patient picker stands in for a real sign-in. All patients are fictional."""
import streamlit as st

st.set_page_config(page_title="Model A", page_icon=":material/favorite:")
nav = st.navigation([
    st.Page("pages/0_Patient_chat.py", title="Patient chat", icon=":material/chat:", default=True),
    st.Page("pages/1_Clinician_queue.py", title="Clinician queue", icon=":material/stethoscope:"),
])
nav.run()

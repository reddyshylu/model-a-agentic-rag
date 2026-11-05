"""Model A chat page (Streamlit). Type or speak a question; read or listen to the answer.

    streamlit run app.py
DEMO ONLY: the patient picker stands in for a real sign-in. All patients are fictional.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a import speech  # noqa: E402
from model_a.monitoring import patient_messages  # noqa: E402
from model_a.pipeline import ModelA  # noqa: E402




@st.cache_resource
def get_model():
    return ModelA()


model = get_model()
patients = model.store.patients

with st.sidebar:
    st.subheader("Demo sign-in")
    st.caption("Fictional patients only. A real app would use a real login.")
    pid = st.selectbox("Patient", sorted(patients),
                       format_func=lambda p: f"{p}  {patients[p]['first_name']} {patients[p]['last_name']}")
    auto_listen = st.toggle("Read answers aloud automatically", value=False)
    st.caption("Playing results aloud: use headphones if you're not alone.")
    if not speech.tts_available():
        st.info("Audio is off until ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID are set. "
                "The spoken text is shown instead.")

# A new session (and an empty chat) whenever the signed-in patient changes
if st.session_state.get("pid") != pid:
    st.session_state.pid = pid
    st.session_state.session = model.start_session(pid)
    st.session_state.chat = []

st.title("Model A")
st.caption(f"Hi {patients[pid]['first_name']}. Ask about your results, medicines, watch or scale data, "
           "or liver health words. For an emergency, call 911.")

# Messages a clinician approved for THIS patient only (nothing pending or rejected)
msgs = patient_messages(pid)
if msgs:
    with st.container(border=True):
        st.markdown(f":material/mail: **Messages from your care team** ({len(msgs)})")
        for m in msgs[:3]:
            st.write(m["message"])
            st.caption(f"Approved by your care team · {m['time'][:10]}")


def render(turn, i):
    with st.chat_message("user"):
        st.write(turn["q"] + ("  :material/mic:" if turn["spoken_q"] else ""))
    with st.chat_message("assistant"):
        if turn["route"] == "red_flag":
            st.error(turn["a"], icon=":material/emergency:")
        else:
            st.write(turn["a"])
        if turn["sources"]:
            with st.expander("Sources"):
                st.write(", ".join(dict.fromkeys(turn["sources"])))
        col = st.container()
        if col.button("Listen", key=f"listen{i}", icon=":material/volume_up:") or turn.get("play"):
            turn["play"] = False
            audio = speech.text_to_speech(turn["spoken"])
            if audio:
                st.audio(audio, format="audio/mpeg", autoplay=True)
            else:
                st.caption(f"Spoken version: {turn['spoken']}")


def ask(question, spoken_q):
    ans = model.ask(st.session_state.session, question)
    spoken = speech.spoken_version(ans.text, ans.route)
    st.session_state.chat.append({"q": question, "a": ans.text, "route": ans.route, "sources": ans.sources,
                                  "spoken": spoken, "spoken_q": spoken_q,
                                  "play": spoken_q or auto_listen or ans.route == "red_flag"})


for i, turn in enumerate(st.session_state.chat):
    render(turn, i)

# Speak a question: transcribe, show the text so the patient can check it, then answer
voice_q = st.audio_input("Or ask by voice", key=f"mic{len(st.session_state.chat)}")
if voice_q is not None:
    text = speech.speech_to_text(voice_q.getvalue())
    if text:
        ask(text, spoken_q=True)
        st.rerun()
    else:
        st.warning("Sorry, I couldn't understand the recording (or speech-to-text is not set up). Please type instead.")

typed = st.chat_input("Type your question")
if typed:
    ask(typed, spoken_q=False)
    st.rerun()

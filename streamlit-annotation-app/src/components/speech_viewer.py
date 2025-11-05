from streamlit import st

def display_speech(speech_text, context):
    st.header("Speech Viewer")
    st.subheader("Context")
    st.write(context)
    st.subheader("Speech Text")
    st.write(speech_text)
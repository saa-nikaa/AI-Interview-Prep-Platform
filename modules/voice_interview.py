import random
import streamlit as st
import speech_recognition as sr
from io import BytesIO
from st_audiorec import st_audiorec
from modules.llm import generate_text
from modules.question_generator import simple_hr_questions

def render_voice_interview(ss):
    """
    Renders the Voice Interview tab with live microphone support.
    """
    st.subheader("🎤 AI Voice Interview Simulator")
    st.info("Simulate a real interview interaction. Speak your answer, and the AI will evaluate it.")

    # --- 1. Generate Question ---
    if st.button("Generate Interview Question"):
        # FAST MODE: Use pre-defined questions instead of slow LLM
        qs = simple_hr_questions(ss.role, ss.level, 5)
        # Pick a random one from the batch
        q = random.choice(qs) if qs else "Tell me about yourself."
        
        ss.vi_question = q
        # Reset previous answer state
        ss.vi_transcript = ""
        ss.vi_last_feedback = {}

    if ss.vi_question:
        st.markdown(f"### 🗣️ Question: {ss.vi_question}")
    else:
        st.warning("Click 'Generate Interview Question' to start.")
        return

    st.markdown("---")
    
    # --- 2. Record Answer ---
    st.write("### 🎙️ Record Your Answer")
    
    # Live Audio Recording
    wav_audio_data = st_audiorec()

    if wav_audio_data is not None:
        st.success("Audio recorded successfully!")
        
        if st.button("Analyze Recording"):
            with st.spinner("Transcribing..."):
                text = transcribe_audio(wav_audio_data)
            
            if text:
                ss.vi_transcript = text
                st.write(f"**📝 Transcript:** {text}")
                
                # Generate Feedback
                with st.spinner("Analyzing answer..."):
                    ss.vi_last_feedback = generate_feedback(ss.vi_question, text)
            else:
                st.error("Could not understand audio. Please try speaking clearer or closer to the mic.")

    # --- 3. Display Feedback ---
    if ss.vi_last_feedback:
        fb = ss.vi_last_feedback
        st.markdown("### 💡 AI Feedback")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clarity", fb.get("Clarity", "N/A"))
        c2.metric("Relevance", fb.get("Relevance", "N/A"))
        c3.metric("Completeness", fb.get("Completeness", "N/A"))
        c4.metric("Overall", fb.get("Overall", "N/A"))
        
        st.markdown("#### Detailed Analysis")
        st.write(fb.get("Feedback", "No detailed feedback generated."))
        
        if fb.get("Improvement"):
            st.markdown("#### 🚀 How to Improve")
            st.info(fb.get("Improvement"))


def transcribe_audio(wav_data):
    """
    Transcribes WAV bytes to text using SpeechRecognition.
    """
    r = sr.Recognizer()
    try:
        # Load WAV data from bytes
        audio_file = BytesIO(wav_data)
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        
        # Recognize using Google Web Speech API (free, no key needed)
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"Speech Service Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None


def generate_feedback(question, answer):
    """
    Generates structured feedback using the LLM.
    """
    prompt = f"""
    You are an expert technical interviewer. Evaluate the candidate's answer.
    
    Question: {question}
    Answer: {answer}
    
    Provide feedback in the following format:
    Clarity: <Score 1-10>
    Relevance: <Score 1-10>
    Completeness: <Score 1-10>
    Overall: <Score 1-10>
    Feedback: <One paragraph summary>
    Improvement: <Bullet points on how to improve>
    
    Output strictly in this format.
    """
    
    response = generate_text(prompt, max_tokens=300)
    
    # Simple parsing (robustness can be improved)
    feedback_dict = {}
    lines = response.split('\n')
    current_key = "Feedback" 
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.startswith("Clarity:"):
            feedback_dict["Clarity"] = line.split(":", 1)[1].strip()
        elif line.startswith("Relevance:"):
            feedback_dict["Relevance"] = line.split(":", 1)[1].strip()
        elif line.startswith("Completeness:"):
            feedback_dict["Completeness"] = line.split(":", 1)[1].strip()
        elif line.startswith("Overall:"):
            feedback_dict["Overall"] = line.split(":", 1)[1].strip()
        elif line.startswith("Feedback:"):
            feedback_dict["Feedback"] = line.split(":", 1)[1].strip()
            current_key = "Feedback"
        elif line.startswith("Improvement:"):
            feedback_dict["Improvement"] = line.split(":", 1)[1].strip()
            current_key = "Improvement"
        else:
            # Append to last known key's value
            if current_key in feedback_dict:
                feedback_dict[current_key] += " " + line
            else:
                 feedback_dict[current_key] = line

    return feedback_dict

import streamlit as st
import pandas as pd
from streamlit_mic_recorder import speech_to_text
import google.generativeai as genai


genai.configure(api_key="AIzaSyAa2xTKiBXA9QbPNYAXZEvyczDCBftMxL4")

# Sample Questions and Answers
data = {
    'Question': [
        "What is a neural network?",
        "Explain the concept of overfitting.",
        "How does a random forest work?",
        "What is supervised learning?",
        "Describe unsupervised learning.",
        "What is a support vector machine?",
        "How do you handle missing data?",
        "Explain cross-validation.",
        "What is gradient descent?",
        "How does a decision tree work?",
    ]
}
df = pd.DataFrame(data)

st.title("AI Interviewer")
st.markdown("""
Welcome to the **AI Interviewer**!  
This tool helps you practice answering technical questions and provides constructive feedback.
""")

# Initialize session state for question index and answers
if 'question_index' not in st.session_state:
    st.session_state.question_index = -1
if 'text_received' not in st.session_state:
    st.session_state.text_received = []


def next_question():
    st.session_state.question_index += 1
    st.session_state.text_received = []

# Start button instead of checkbox
if st.session_state.question_index == -1:
    if st.button("Start the interview"):
        next_question()
        st.rerun()


# Interview in progress
if st.session_state.question_index >= 0:
    # Ensure the question index is within bounds
    if st.session_state.question_index < len(df):
        question = df.iloc[st.session_state.question_index]["Question"]
        st.markdown("### Question: ")
        st.info(question)

        
        st.markdown("#### Your Answer:")
        text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

        if text:
            st.session_state.text_received.append(text)

            st.text_area("Your Answer So Far:", value=st.session_state.text_received[-1], height=100)

        submit = st.button("Submit Your Answer")

        if submit and st.session_state.text_received:
            st.markdown("### Analyzing your answer...")
            with st.spinner('Waiting for feedback...'):

                # Format the prompt with the provided question and answer
                prompt = (
                    f"The interview question asked is: '{question}'. "
                    f"The answer provided was: '{st.session_state.text_received[-1]}'. "
                    "Could you rate this answer out of 10, and provide detailed feedback on its accuracy, completeness, "
                    "clarity, and how it can be improved?"
                )



                model = genai.GenerativeModel('gemini-1.5-flash')

                # Call to Gemini API for feedback
                response = model.generate_content(prompt)

                # Extract and display the feedback
                feedback_content = response.text


            st.success("Analysis Complete!")

            st.markdown("### Feedback:")
            # Extract rating from feedback content
            rating_start = feedback_content.find('rate this answer ') + len('rate this answer ')
            rating_end = feedback_content.find(' out of 10')
            rating = feedback_content[rating_start:rating_end] if rating_start != -1 and rating_end != -1 else "N/A"
            
            st.markdown(f"**Rating:** {rating} / 10")
            st.markdown(f"**Detailed Feedback:**\n\n{feedback_content}")

            # Buttons to proceed to the next question or end the interview
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next Question",on_click=next_question):
                    st.rerun()

            with col2:
                if st.button("End/Completed"):
                    # st.markdown("### Interview Completed!")
                    # st.markdown("Thank you for participating. You can review your answers and feedback above.")
                    st.session_state.question_index = len(df)  # End the interview
                    st.session_state.text_received = []
                    st.rerun()


    else:
        st.markdown("### Interview Completed!")
        st.markdown("You have answered all the questions. Thank you for participating.")

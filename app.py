import streamlit as st
from dotenv import load_dotenv
from scrape import personalized_budget_answer

# Load environment variables
load_dotenv()

def main():
    st.title("Ask Questions")
    st.subheader("Ex: I'm going to Paris for 5 days on $200")

    user_prompt = st.text_input("Enter prompt")

    if st.button("Submit"):
        with st.spinner("Processing"):
            analysis = personalized_budget_answer(user_prompt)
            st.subheader("Analyzing:")
            st.write(analysis)

if __name__ == "__main__":
    main()
import streamlit as st
import snowflake.connector  # to query Snowflake
import snowflake.snowpark as snowpark
import re

st.set_page_config(page_title="Setup Genie", page_icon="❄️", layout="wide")

conn = st.connection("snowflake")
session = conn.session()
# snowflake_params = st.secrets

# if not st.secrets:
#     st.error("Snowflake connection parameters not found in secrets.toml.")
# else:
#     session = snowpark.Session.builder.configs({
#         "account": snowflake_params["account"],
#         "user": snowflake_params["user"],
#         "password": snowflake_params["password"],
#         "warehouse": snowflake_params["warehouse"],
#         "database": snowflake_params["database"],
#         "schema": snowflake_params["schema"],
#         "role": snowflake_params["role"]
#     }).create()



st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
            color: #333333;
        }
        .stButton>button {
            background-color: #38b6ff;  /* Light blue color */
            color: white;
            border-radius: 12px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #3498db;  /* Slightly darker blue on hover */
        }
        .stTextInput>div>input {
            background-color: #e8f4f9;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #ccc;
            font-size: 16px;
        }
        .stMarkdown {
            font-size: 18px;
            line-height: 1.6;
        }
        .section-header {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 12px;
        }
        .panel {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Setup Genie")

question = st.text_input('Ask a Question', 'My app crashed. What do I do?')

# Define helper functions
def limit_to_4_sentences(response):
    sentences = response.split(". ")
    return ". ".join(sentences[:4]) + ('.' if len(sentences) > 4 else '')

def filter_relevant_content(response):
    patterns_to_exclude = [
        r"Step \d+: .*",
        r"Query \d+: .*",
        r"SELECT .* FROM .*",
        r"Download .*",
        r"Create .*",
        r"Push .*",
        r"Submission Instructions.*",
        r"Grading Rubric.*",
        r"Following these instructions will help you complete the project.*",
        r"SQL Queries with .*",
        r"ERD.*",
        r"List all .*",
        r"Instructions.*",
    ]
    combined_pattern = "|".join(patterns_to_exclude)
    cleaned_response = re.sub(combined_pattern, "", response, flags=re.DOTALL)
    return cleaned_response.strip()

def word_overlap(question, text):
    question_words = set(re.findall(r'\w+', question.lower()))
    text_words = set(re.findall(r'\w+', text.lower()))
    common_words = question_words.intersection(text_words)
    return len(common_words) >= 2

    # Query handling for "Instructions" and "Teacher Notes"
if st.button(":snowflake: Submit", type="primary"):
    # Instructions Section
    with st.expander("📚 Instructions (Only)", expanded=True):
        instructions_query = f"""
            SELECT * FROM TABLE(ASSIGNMENTS_LLM('{question}'));
            """
        instructions_response = session.sql(instructions_query).collect()

        direct_match = None
        for response in instructions_response:
            if word_overlap(question, response['RESPONSE']):
                direct_match = response['RESPONSE']
                break

        if direct_match:
            st.markdown(f'<div class="section-header">Direct Match Found in Assignment Instructions:</div>', unsafe_allow_html=True)
            st.markdown(f"**Response:\n** {filter_relevant_content(direct_match).replace('SQL Queries', '')}")
        else:
            st.markdown(f'<div class="section-header">Recommended actions from review of assignment instructions:</div>', unsafe_allow_html=True)
            filtered_response = filter_relevant_content(instructions_response[0].RESPONSE)
            if filtered_response:
                st.markdown(f"**Response:\n** {limit_to_4_sentences(filtered_response)}")
            else:
                st.markdown("No relevant instructions found.")

    # Teacher Notes Section
    with st.expander("👩‍🏫 Teacher Notes (Only)", expanded=True):
        notes_query = f"""
            SELECT problem_reported, resolution_notes
            FROM teacher_notes
            """
        notes_response = session.sql(notes_query).collect()

        direct_match = None
        for note in notes_response:
            if word_overlap(question, note['PROBLEM_REPORTED']):
                direct_match = note['RESOLUTION_NOTES']
                break

        if direct_match:
            st.markdown(f'<div class="section-header">Direct Match Found in Teacher Notes:</div>', unsafe_allow_html=True)
            st.markdown(f"**Response:** {direct_match}")
        else:
            st.markdown(f'<div class="section-header">Recommended actions from teacher notes:</div>', unsafe_allow_html=True)
            if notes_response:
                relevant_notes = [note['RESOLUTION_NOTES'] for note in notes_response]
                st.markdown(f"**Response:** {limit_to_4_sentences(' '.join(relevant_notes))}")
            else:
                st.markdown("No relevant teacher notes found.")

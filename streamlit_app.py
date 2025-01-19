
import streamlit as st
import snowflake.connector  # to query Snowflake
import snowflake.snowpark as snowpark
import re

st.set_page_config(page_title="Assignment Assistant", page_icon="❄️", layout="wide")

conn = st.connection("snowflake")
session = conn.session()

st.markdown("""
    <style>
        body {
            background-color: #e0f7fa;
            color: #000033;
        }

        .stButton>button {
            background-color: #1D7EA4; 
            color: #FFDA03;
            border-radius: 12px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0074D9;
        }

        .stTextInput>div>input {
            background-color: #b3ecff;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #2596be;
            font-size: 16px;
        }

        .box {
            border-radius: 12px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .box-instructions {
            background-color: #2596be;
            color: #FFDA03;
        }
        .box-notes {
            background-color: #FFDA03;
            color: #2596be;
        }
        .section-header {
            font-size: 20px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

st.title(":blue[Assignment Assistant] :student::handshake::computer:")

question = st.text_input(':blue[Ask A2 a Question!]', 'My app crashed. What do I do?')

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

# Display buttons and side-by-side results
if st.button(":snowflake: Submit", type="primary"):
    # Instructions Section
    instructions_query = f"SELECT * FROM TABLE(ASSIGNMENTS_LLM('{question}'));"
    instructions_response = session.sql(instructions_query).collect()

    direct_match_instructions = None
    for response in instructions_response:
        if word_overlap(question, response['RESPONSE']):
            direct_match_instructions = response['RESPONSE']
            break

    instructions_text = (
        filter_relevant_content(direct_match_instructions)
        if direct_match_instructions
        else filter_relevant_content(instructions_response[0].RESPONSE)
        if instructions_response
        else "No relevant instructions found."
    )

    # Teacher Notes Section
    notes_query = "SELECT problem_reported, resolution_notes FROM teacher_notes"
    notes_response = session.sql(notes_query).collect()

    direct_match_notes = None
    for note in notes_response:
        if word_overlap(question, note['PROBLEM_REPORTED']):
            direct_match_notes = note['RESOLUTION_NOTES']
            break

    notes_text = (
        direct_match_notes
        if direct_match_notes
        else limit_to_4_sentences(
            " ".join(note['RESOLUTION_NOTES'] for note in notes_response)
        )
        if notes_response
        else "No relevant teacher notes found."
    )

    # Render side-by-side boxes
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div class='box box-instructions'><div class='section-header'>📚 Instructions:</div>{instructions_text}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='box box-notes'><div class='section-header'>👩‍🏫 Teacher Notes:</div>{notes_text}</div>", unsafe_allow_html=True)

# import streamlit as st
# import snowflake.connector  # to query Snowflake
# import snowflake.snowpark as snowpark
# import re

# st.set_page_config(page_title="Assignment Assistant", page_icon="❄️", layout="wide")

# conn = st.connection("snowflake")
# session = conn.session()

# st.markdown("""
#     <style>
#         body {
#             background-color: #e0f7fa;
#             color: #000033;
#         }

#         .stButton>button {
#             background-color: #0074D9; 
#             color: #FFDC00;
#             border-radius: 12px;
#             padding: 10px 20px;
#             font-size: 16px;
#             border: none;
#         }
#         .stButton>button:hover {
#             background-color: #001F3F;
#         }

#         .stTextInput>div>input {
#             background-color: #b3ecff;
#             border-radius: 8px;
#             padding: 10px;
#             border: 1px solid #0074D9;
#             font-size: 16px;
#         }

#         .box {
#             border-radius: 12px;
#             padding: 20px;
#             margin: 10px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         }
#         .box-instructions {
#             background-color: #0074D9;
#             color: #FFDC00;
#         }
#         .box-notes {
#             background-color: #FFDC00;
#             color: #0074D9;
#         }
#         .section-header {
#             font-size: 20px;
#             font-weight: bold;
#         }
#     </style>
#     """, unsafe_allow_html=True)

# st.title(":blue[Assignment Assistant] :student::handshake::computer:")

# question = st.text_input(':blue[Ask A2 a Question!]', 'My app crashed. What do I do?')

# # Define helper functions
# def limit_to_4_sentences(response):
#     sentences = response.split(". ")
#     return ". ".join(sentences[:4]) + ('.' if len(sentences) > 4 else '')

# def filter_relevant_content(response):
#     patterns_to_exclude = [
#         r"Step \d+: .*",
#         r"Query \d+: .*",
#         r"SELECT .* FROM .*",
#         r"Download .*",
#         r"Create .*",
#         r"Push .*",
#         r"Submission Instructions.*",
#         r"Grading Rubric.*",
#         r"Following these instructions will help you complete the project.*",
#         r"SQL Queries with .*",
#         r"ERD.*",
#         r"List all .*",
#         r"Instructions.*",
#     ]
#     combined_pattern = "|".join(patterns_to_exclude)
#     cleaned_response = re.sub(combined_pattern, "", response, flags=re.DOTALL)
#     return cleaned_response.strip()

# def word_overlap(question, text):
#     question_words = set(re.findall(r'\w+', question.lower()))
#     text_words = set(re.findall(r'\w+', text.lower()))
#     common_words = question_words.intersection(text_words)
#     return len(common_words) >= 2

# # Display buttons and side-by-side results
# if st.button(":snowflake: Submit", type="primary"):
#     # Instructions Section
#     instructions_query = f"SELECT * FROM TABLE(ASSIGNMENTS_LLM('{question}'));"
#     instructions_response = session.sql(instructions_query).collect()

#     direct_match_instructions = None
#     for response in instructions_response:
#         if word_overlap(question, response['RESPONSE']):
#             direct_match_instructions = response['RESPONSE']
#             break

#     instructions_text = (
#         filter_relevant_content(direct_match_instructions)
#         if direct_match_instructions
#         else filter_relevant_content(instructions_response[0].RESPONSE)
#         if instructions_response
#         else "No relevant instructions found."
#     )

#     # Teacher Notes Section
#     notes_query = "SELECT problem_reported, resolution_notes FROM teacher_notes"
#     notes_response = session.sql(notes_query).collect()

#     direct_match_notes = None
#     for note in notes_response:
#         if word_overlap(question, note['PROBLEM_REPORTED']):
#             direct_match_notes = note['RESOLUTION_NOTES']
#             break

#     notes_text = (
#         direct_match_notes
#         if direct_match_notes
#         else limit_to_4_sentences(
#             " ".join(note['RESOLUTION_NOTES'] for note in notes_response)
#         )
#         if notes_response
#         else "No relevant teacher notes found."
#     )

#     # Render side-by-side boxes
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown(f"<div class='box box-instructions'><div class='section-header'>📚 Instructions:</div>{instructions_text}</div>", unsafe_allow_html=True)

#     with col2:
#         st.markdown(f"<div class='box box-notes'><div class='section-header'>👩‍🏫 Teacher Notes:</div>{notes_text}</div>", unsafe_allow_html=True)


####################

# import streamlit as st
# import snowflake.connector  # to query Snowflake
# import snowflake.snowpark as snowpark
# import re

# st.set_page_config(page_title="Assignment Assistant", page_icon="❄️", layout="wide")

# conn = st.connection("snowflake")
# session = conn.session()

# st.markdown("""
#     <style>
        
#         body {
#             background-color: #f0f8ff;
#             color: #333333;
#         }
            
#         .streamlit-expanderHeader {
#         font-color: #2596be; 
#         font-size: 24px; 
#         font-weight: bold;
#     }
#         .streamlit-expanderContent {
#             background-color: #2596be;
#             color: #2596be; # Expander content color
#         }
#         .stButton>button {
#             background-color: #38b6ff; 
#             color: white;
#             border-radius: 12px;
#             padding: 10px 20px;
#             font-size: 16px;
#             border: none;
#         }
#         .stButton>button:hover {
#             background-color: #3498db;  
#         }
#         .stTextInput>div>input {
#             background-color: #e8f4f9;
#             border-radius: 8px;
#             padding: 10px;
#             border: 1px solid #ccc;
#             font-size: 16px;
#         }
        

#         .stMarkdown {
#             font-size: 18px;
#             line-height: 1.6;
#         }
#         .section-header {
#             font-size: 20px;
#             font-weight: bold;
#             color: #2c3e50;
#             margin-bottom: 12px;
#         }
#         .panel {
#             background-color: #ffffff;
#             border-radius: 12px;
#             padding: 20px;
#             margin-bottom: 20px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         }
#     </style>
#     """, unsafe_allow_html=True)

# st.title(":blue[Assignment Assistant] :student::handshake::computer:")


# question = st.text_input(':orange-background[Ask A2 a Question!]', 'My app crashed. What do I do?')

# # Define helper functions
# def limit_to_4_sentences(response):
#     sentences = response.split(". ")
#     return ". ".join(sentences[:4]) + ('.' if len(sentences) > 4 else '')

# def filter_relevant_content(response):
#     patterns_to_exclude = [
#         r"Step \d+: .*",
#         r"Query \d+: .*",
#         r"SELECT .* FROM .*",
#         r"Download .*",
#         r"Create .*",
#         r"Push .*",
#         r"Submission Instructions.*",
#         r"Grading Rubric.*",
#         r"Following these instructions will help you complete the project.*",
#         r"SQL Queries with .*",
#         r"ERD.*",
#         r"List all .*",
#         r"Instructions.*",
#     ]
#     combined_pattern = "|".join(patterns_to_exclude)
#     cleaned_response = re.sub(combined_pattern, "", response, flags=re.DOTALL)
#     return cleaned_response.strip()

# def word_overlap(question, text):
#     question_words = set(re.findall(r'\w+', question.lower()))
#     text_words = set(re.findall(r'\w+', text.lower()))
#     common_words = question_words.intersection(text_words)
#     return len(common_words) >= 2

#     # Query handling for "Instructions" and "Teacher Notes"
# if st.button(":snowflake: Submit", type="primary"):
#     # Instructions Section
#     with st.expander("📚 Notes from Assignment Instructions ", expanded=True):
#         instructions_query = f"""
#             SELECT * FROM TABLE(ASSIGNMENTS_LLM('{question}'));
#             """
#         instructions_response = session.sql(instructions_query).collect()

#         direct_match = None
#         for response in instructions_response:
#             if word_overlap(question, response['RESPONSE']):
#                 direct_match = response['RESPONSE']
#                 break

#         if direct_match:
#             #st.markdown(f'<div class="section-header">Direct Match Found in Assignment Instructions:</div>', unsafe_allow_html=True)
#             st.markdown(f"**Response:\n** {filter_relevant_content(direct_match).replace('SQL Queries', '')}")
#         else:
#             st.markdown(f'<div class="section-header">Recommended actions from review of assignment instructions:</div>', unsafe_allow_html=True)
#             filtered_response = filter_relevant_content(instructions_response[0].RESPONSE)
#             if filtered_response:
#                 st.markdown(f"**Response:\n** {limit_to_4_sentences(filtered_response)}")
#             else:
#                 st.markdown("No relevant instructions found.")

#     # Teacher Notes Section
#     with st.expander("👩‍🏫 Teacher and TA Notes", expanded=True):
#         notes_query = f"""
#             SELECT problem_reported, resolution_notes
#             FROM teacher_notes
#             """
#         notes_response = session.sql(notes_query).collect()

#         direct_match = None
#         for note in notes_response:
#             if word_overlap(question, note['PROBLEM_REPORTED']):
#                 direct_match = note['RESOLUTION_NOTES']
#                 break

#         if direct_match:
#             #st.markdown(f'<div class="section-header"></div>', unsafe_allow_html=True)
#             st.markdown(f"**Response:** {direct_match}")
#         else:
#             #st.markdown(f'<div class="section-header">Recommended actions from teacher notes:</div>', unsafe_allow_html=True)
#             if notes_response:
#                 relevant_notes = [note['RESOLUTION_NOTES'] for note in notes_response]
#                 st.markdown(f"**Response:** {limit_to_4_sentences(' '.join(relevant_notes))}")
#             else:
#                 st.markdown("No relevant teacher notes found.")

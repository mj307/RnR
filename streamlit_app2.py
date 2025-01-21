import streamlit as st
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
import os
from snowflake.core import Root
from typing import List
from snowflake.cortex import complete
from trulens.apps.custom import instrument
from trulens.providers.cortex.provider import Cortex
from trulens.core import Feedback
from trulens.core import Select
import numpy as np
from trulens.apps.custom import TruCustomApp
from trulens.core import TruSession
from trulens.connectors.snowflake import SnowflakeConnector


load_dotenv()

st.set_page_config(page_title="Assignment Assistant", page_icon="❄️", layout="wide")

connection_params = {
    "account":  os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_USER_PASSWORD"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
}



class CortexSearchRetriever:
    def __init__(self, snowpark_session, limit_to_retrieve):
        self._snowpark_session = snowpark_session
        self._limit_to_retrieve = limit_to_retrieve

    def retrieve(self, query: str) -> List[str]:
        root = Root(self._snowpark_session)
        cortex_search_service = (
            root.databases[os.getenv("SNOWFLAKE_DATABASE")]
                .schemas[os.getenv("SNOWFLAKE_SCHEMA")]
                .cortex_search_services[os.getenv("SNOWFLAKE_CORTEX_SEARCH_SERVICE")]
            # need to create a second .cortex_search_service for the second service (teacher notes, since i only have
            # for assignments rn)
        )
        resp = cortex_search_service.search(
            query=query,
            columns=["CHUNK_TEXT"],
            limit=self._limit_to_retrieve,
        )

        if resp.results:
            return [curr["CHUNK_TEXT"] for curr in resp.results]
        else:
            return []



class RAG:
    def __init__(self):
        self.retriever = CortexSearchRetriever(snowpark_session=snowpark_session, limit_to_retrieve=4)

    @instrument
    def retrieve_context(self, query: str) -> List[str]:
        """
        Retrieve relevant text from Snowflake Cortex.
        """
        return self.retriever.retrieve(query)

    @instrument
    def generate_completion(self, query: str, context_str: List[str]) -> str:
        context = "\n".join(context_str)
        prompt = f"""
          You are an assignment assistant extracting information from the context provided.
          Answer the question based on the context. Be concise and do not hallucinate.
          If you don’t have the information, just say so.
          Context: {context}
          Question:
          {query}
          Answer:
        """
        return complete("mistral-large2", prompt) #.get("result")

    @instrument
    def query(self, query: str) -> str:
        """
        Perform the retrieval and generation in a single query flow.
        """
        context_str = self.retrieve_context(query)
        return self.generate_completion(query, context_str)

    @instrument
    def generate_completion_val(self, query: str, context_str: List[str]) -> str:
        context = "\n".join(context_str)
        prompt = f"""
          You are an assignment assistant extracting information from the context provided.
          Answer the question based on the context. Be as creative as you want and use poetry to answer.
          If you don’t have the information, write a haiku. 
          Context: {context}
          Question:
          {query}
          Answer:
        """
        return complete("mistral-large2", prompt) #.get("result")

    @instrument
    def query_val(self, query: str) -> str:
        """
        Perform the retrieval and generation in a single query flow.
        """
        context_str = self.retrieve_context(query)
        return self.generate_completion_val(query, context_str)


snowpark_session = Session.builder.configs(connection_params).getOrCreate()

tru_snowflake_connector = SnowflakeConnector(snowpark_session=snowpark_session)
tru_session = TruSession(connector=tru_snowflake_connector)
provider = Cortex(snowpark_session, "llama3.1-8b")

f_groundedness = (
    Feedback(provider.groundedness_measure_with_cot_reasons, name="Groundedness")
        .on(Select.RecordCalls.retrieve_context.rets[:].collect())
        .on_output()
)

f_context_relevance = (
    Feedback(provider.context_relevance, name="Context Relevance")
        .on_input()
        .on(Select.RecordCalls.retrieve_context.rets[:])
        .aggregate(np.mean)
)

f_answer_relevance = (
    Feedback(provider.relevance, name="Answer Relevance")
        .on_input()
        .on_output()
        .aggregate(np.mean)
)

rag = RAG()
# query = "How do I get Postgres to work?"
# answer = rag.query(query)
# print (answer)
# print ('###########################')
# query = "I have public IP checked. Why is my code not working?"
# answer = rag.query(query)
# print (answer)


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
        .box-instructions-val {
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

question = st.text_input(':blue[Ask A2 a Question!]', 'I have public IP checked but my code is not working. How do I fix this?')

# one box with instructions notes as of now -- will fix later to incorporate teacher notes too

tru_rag = TruCustomApp(
    rag,
    app_name="RAG",
    app_version="production",
    feedbacks=[f_groundedness, f_answer_relevance, f_context_relevance]
)

rag_val = RAG()
tru_rag_val = TruCustomApp(
    rag_val,
    app_name="RAG",
    app_version="validation",
    feedbacks=[f_groundedness, f_answer_relevance, f_context_relevance]
)

if st.button(":snowflake: Submit", type="primary"):
    #rag = RAG()
    #instructions_text = rag.query(question)
    #st.markdown(f"<div class='box box-instructions'><div class='section-header'>📚 Instructions:</div>{instructions_text}</div>", unsafe_allow_html=True)

    with tru_rag as recording:
        instructions_text = rag.query(question)
    st.markdown(f"<div class='box box-instructions'><div class='section-header'>📚 Instructions:</div>{instructions_text}</div>", unsafe_allow_html=True)

    st.write("The response below are generated with a different prompt, which encourages creativity, to test out Trulens.")
    with tru_rag_val as recording:
        instructions_text_val = rag_val.query_val(question)
    st.markdown(f"<div class='box box-instructions-val'><div class='section-header'>📚 Instructions Val:</div>{instructions_text_val}</div>", unsafe_allow_html=True)


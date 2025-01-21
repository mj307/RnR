# 📚 Assignment Assistant

## Inspiration
As a college student, one of the most challenging aspects of assignments is parsing and remembering the specifics and the nuances from a long assignment. Going to office hours may help, there’s often a long line, and students end up wasting a lot of time. Additionally, TA's and Professors have to spend a lot of their time explaining the same question to multiple students, wasting their time. This is frustrating for both students, TAs, and Professors.

## Introducing ... A2!
Assignment Assistant, or A2, is an AI-Powered assistant that allows TAs and professors to upload assignments, troubleshooting notes, and solutions to a shared platform. Students can then search through these past solutions and assignment specifics to quickly find answers to common clarification questions or setup issues, thus helping them make progress independently.

## Design
- Use Snowflake Stage to upload assignments in PDF format
- Create table using the stage
- Parse and chunk assignments/solutions PDF and store in table
- Parse and chunk past student questions and TA assisted solutions from past years into the table
- Create Snowflake Cortex Search Service to vectorize and index the chunked data from above 2 steps
- Leverage Mistral-Large2 LLM to build RAG with context coming from Cortex Search Service
- Streamlit for frontend and Streamlit Community Cloud for deployment
- Trulens Evaluation Framework to A/B test different prompts to improve groundedness, context relevance, and answer relevance


## Future Work
- Enhance UI to include additional filteration such as course, professor, etc
- Provide citations for the solutions
- Add additional attributes for filtering from Cortex Search Service to improve the generated responses to improve accuracy and performance
  


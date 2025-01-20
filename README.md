# 📚 Assignment Assistant

## Inspiration
As a college student taking multiple computer science courses, I’ve noticed that one of the most challenging aspects of assignments is setting up the environment and code. When I’ve gone to office hours to get help, there’s often a long line, and with office hours being limited to just an hour or two, teaching assistants (TAs) don’t always have enough time to assist everyone. This creates a bottleneck, forcing students to wait until the last minute to get the help they need, which is frustrating for both students and TAs.

## Introducing ... A2!
Assignment Assisstant, or A2, is a tool that allows TAs and professors to upload troubleshooting notes and solutions to a shared platform. Students can then search through these past solutions to quickly find answers to common setup issues, helping them troubleshoot more efficiently and independently.

## How I built it
I used Snowflake for backend and Streamlit Community Cloud for front end. For the backend, I first set up a database and a schema to store all my assignment data in Snowflake's SQL Worksheets. I created a function that allows the app to read and extract text from uploaded PDF assignments. Then, I chunked the assignment text into smaller pieces and used vector embeddings to convert these chunks into numerical representations. This allows the app to perform a cosine similarity search, helping to match relevant content to user queries. Finally, I created a search service to help users quickly find relevant assignment information. For the front end, I wanted a very welcoming and academically oriented color scheme, which is why I chose a blue and yellow theme. Using Streamlit, I created a text input box, allowing the user to submit questions about their assignments. Once the Submit button is hit, the app will generate two boxes: one having information on how to resolve the issue, directly from the assignment instructions, and the second have information on how to resolve the issue, coming from the teacher notes. This way the user gets a well rounded response to help them fix their set up problem.


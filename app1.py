# import streamlit as st
# from langchain.agents import create_sql_agent
# from langchain.sql_database import SQLDatabase
# from langchain.agents.agent_types import AgentType
# from langchain.callbacks import StreamlitCallbackHandler
# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from sqlalchemy import create_engine
# import os
# from urllib.parse import quote_plus
# from dotenv import load_dotenv
# from langchain.chat_models import ChatOpenAI

# # Load environment variables
# load_dotenv()

# st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🥜")
# st.title("🥜 LangChain: Chat with SQL DB (Optimized)")

# # ========== SIDEBAR INPUTS FOR POSTGRESQL CREDENTIALS ==========
# st.sidebar.header("PostgreSQL Configuration")
# pg_host = st.sidebar.text_input("PostgreSQL Host", "localhost")
# pg_port = st.sidebar.text_input("PostgreSQL Port", "5432")
# pg_user = st.sidebar.text_input("PostgreSQL User")
# pg_password = st.sidebar.text_input("PostgreSQL Password", type="password")
# pg_db = st.sidebar.text_input("PostgreSQL Database Name")

# # ========== FETCH OPENAI API KEY ==========
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     st.error("OpenAI API key is not set. Please configure it in the environment variables.")
#     st.stop()

# # ========== LLM MODEL ==========
# llm = ChatOpenAI(
#     openai_api_key=api_key,
#     model="gpt-3.5-turbo",
#     temperature=0,  # Makes output deterministic
#     streaming=False  # Disable streaming for a single complete response
# )

# @st.cache_resource(ttl="2h")
# def configure_db(pg_host, pg_port, pg_user, pg_password, pg_db):
#     """Create and return a SQLDatabase connected to PostgreSQL."""
#     if not (pg_host and pg_port and pg_user and pg_password and pg_db):
#         st.error("Please provide all PostgreSQL connection details.")
#         st.stop()

#     try:
#         # Encode the password to handle special characters
#         encoded_password = quote_plus(pg_password)
#         postgres_uri = f"postgresql+psycopg2://{pg_user}:{encoded_password}@{pg_host}:{pg_port}/{pg_db}"
#         return SQLDatabase(create_engine(postgres_uri))
#     except Exception as e:
#         st.error(f"Database connection failed: {e}")
#         st.stop()

# # ========== CONFIGURE POSTGRESQL DATABASE ==========
# db = configure_db(pg_host, pg_port, pg_user, pg_password, pg_db)

# # ========== TOOLKIT & AGENT ==========
# prefix = (
#     "You are a highly skilled database assistant with full SQL privileges. "
#     "Your primary function is to provide accurate, concise, and timely answers to user queries related to the database. "
#     "You may execute SQL queries as needed, but the user should only see the final, processed results. "
#     "Avoid displaying intermediate steps, unnecessary technical details, or sensitive information unless explicitly requested. "
#     "If the user requests an update or change to the database, provide a clear and explicit confirmation statement before proceeding, "
#     "including the scope of changes, potential effects, and any necessary warnings or caveats. "
#     "Always prioritize data accuracy, integrity, security, and consistency in your responses, "
#     "and adhere to best practices for data protection, backups, and recovery. "
#     "If you're unsure about the user's intent, request clarification or additional information before proceeding. "
#     "Provide clear and concise explanations for any errors, exceptions, or unexpected results, "
#     "and offer suggestions for alternative queries or approaches as needed. "
#     "Maintain a professional tone, use proper SQL syntax and terminology, "
#     "and ensure that your responses are easy to understand and follow."
# )

# toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# agent = create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     prefix=prefix,
#     handle_parsing_errors=True  # Ensures retries on parsing failures
# )

# # ========== MESSAGE HISTORY ==========
# if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
#     st.session_state["messages"] = [
#         {"role": "assistant", "content": "Hello! How can I assist you with your database today?"}
#     ]

# for msg in st.session_state["messages"]:
#     st.chat_message(msg["role"]).write(msg["content"])

# # ========== USER QUERY ==========
# user_query = st.chat_input(placeholder="Ask or command anything (e.g. SELECT, UPDATE, DELETE...)")

# if user_query:
#     # Record user message
#     st.session_state["messages"].append({"role": "user", "content": user_query})
#     st.chat_message("user").write(user_query)

#     # Send query to agent with a loader
#     with st.chat_message("assistant"):
#         with st.spinner("Generating response..."):
#             try:
#                 response = agent.run(user_query)
#                 st.session_state["messages"].append({"role": "assistant", "content": response})
#                 st.write(response)
#             except ValueError as e:
#                 st.error(f"Parsing error occurred: {str(e)}")


import streamlit as st
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# Load environment variables
load_dotenv()

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🥜")
st.title("🥜 LangChain: Chat with SQL DB (Optimized)")

# ========== SIDEBAR INPUTS FOR POSTGRESQL CREDENTIALS ==========
st.sidebar.header("PostgreSQL Configuration")
pg_host = st.sidebar.text_input("PostgreSQL Host", "localhost")
pg_port = st.sidebar.text_input("PostgreSQL Port", "5432")
pg_user = st.sidebar.text_input("PostgreSQL User")
pg_password = st.sidebar.text_input("PostgreSQL Password", type="password")
pg_db = st.sidebar.text_input("PostgreSQL Database Name")

# Manual refresh button to update the database connection (and agent) when needed.
refresh_db = st.sidebar.button("Refresh Database Connection")

# ========== FETCH OPENAI API KEY ==========
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not set. Please configure it in the environment variables.")
    st.stop()

# ========== LLM MODEL ==========
llm = ChatOpenAI(
    openai_api_key=api_key,
    model="gpt-3.5-turbo",
    temperature=0,  # Makes output deterministic
    streaming=False  # Disable streaming for a single complete response
)

@st.cache_resource(ttl="2h")
def configure_db(pg_host, pg_port, pg_user, pg_password, pg_db):
    """Create and return a SQLDatabase connected to PostgreSQL."""
    if not (pg_host and pg_port and pg_user and pg_password and pg_db):
        st.error("Please provide all PostgreSQL connection details.")
        st.stop()

    try:
        # Encode the password to handle special characters
        encoded_password = quote_plus(pg_password)
        postgres_uri = f"postgresql+psycopg2://{pg_user}:{encoded_password}@{pg_host}:{pg_port}/{pg_db}"
        return SQLDatabase(create_engine(postgres_uri))
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

# ========== CONFIGURE POSTGRESQL DATABASE ==========
db = configure_db(pg_host, pg_port, pg_user, pg_password, pg_db)

# ========== TOOLKIT & AGENT SETUP ==========
prefix = (
    "You are a highly skilled database assistant with full SQL privileges. "
    "Your primary function is to provide accurate, concise, and timely answers to user queries related to the database. "
    "You may execute SQL queries as needed, but the user should only see the final, processed results. "
    "Avoid displaying intermediate steps, unnecessary technical details, or sensitive information unless explicitly requested. "
    "If the user requests an update or change to the database, provide a clear and explicit confirmation statement before proceeding, "
    "including the scope of changes, potential effects, and any necessary warnings or caveats. "
    "Always prioritize data accuracy, integrity, security, and consistency in your responses, "
    "and adhere to best practices for data protection, backups, and recovery. "
    "If you're unsure about the user's intent, request clarification or additional information before proceeding. "
    "Provide clear and concise explanations for any errors, exceptions, or unexpected results, "
    "and offer suggestions for alternative queries or approaches as needed. "
    "Maintain a professional tone, use proper SQL syntax and terminology, "
    "and ensure that your responses are easy to understand and follow."
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    prefix=prefix,
    handle_parsing_errors=True  # Ensures retries on parsing failures
)

# ========== MANUAL DATABASE REFRESH ==========
if refresh_db:
    # Clear the cached database connection
    configure_db.clear()
    # Reinitialize the connection, toolkit, and agent
    db = configure_db(pg_host, pg_port, pg_user, pg_password, pg_db)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=prefix,
        handle_parsing_errors=True,
    )
    st.sidebar.success("Database connection refreshed.")

# ========== MESSAGE HISTORY ==========
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! How can I assist you with your database today?"}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# ========== USER QUERY ==========
user_query = st.chat_input(placeholder="Ask or command anything (e.g. SELECT, UPDATE, DELETE...)")

if user_query:
    # Record user message
    st.session_state["messages"].append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Send query to agent with a loader
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                response = agent.run(user_query)
                st.session_state["messages"].append({"role": "assistant", "content": response})
                st.write(response)
            except ValueError as e:
                st.error(f"Parsing error occurred: {str(e)}")

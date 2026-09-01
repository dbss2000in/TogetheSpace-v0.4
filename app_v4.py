import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(
    page_title="TogetheSpace v0.4 — High Concurrency Hub", page_icon="⚡", layout="wide"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

@st.cache_resource
def get_db_engine():
    return create_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True)

try:
    engine = get_db_engine()
except Exception as e:
    st.error(f"Database connection error: {e}")

st.title("⚡ TogetheSpace v0.4 (High-Concurrency Edition)")
st.info("System optimized for heavy traffic loads via PostgreSQL connection pooling.")

@st.cache_data(ttl=10)
def load_data_resilient(query):
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, con=conn)
    except Exception as e:
        return pd.DataFrame()

df_test = load_data_resilient("SELECT 1 as status;")
if not df_test.empty:
    st.success("Database connection pool is active and stable.")
else:
    st.warning("Please configure your DATABASE_URL environment variable to connect to PostgreSQL.")

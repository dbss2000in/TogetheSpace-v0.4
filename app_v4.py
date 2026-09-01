import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- SCALABLE POSTGRESQL CONNECTION POOLING ---
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:TogetheSpace2026Secure@db.misgnchymprfkgxvrxqm.supabase.co:5432/postgres',
)

st.title('⚡ TogetheSpace v0.4 (High-Concurrency Edition)')
st.info('System optimized for heavy traffic loads via PostgreSQL connection pooling.')

@st.cache_resource
def get_db_engine(url):
  return create_engine(url, pool_size=20, max_overflow=10, pool_pre_ping=True)

try:
  engine = get_db_engine(DATABASE_URL)
  with engine.connect() as conn:
    df_test = pd.read_sql('SELECT 1 as status;', con=conn)
  
  if not df_test.empty:
    st.success('Database connection pool is active and stable.')
except Exception as e:
  st.error(f'Connection failed. Details: {e}')

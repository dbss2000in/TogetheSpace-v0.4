import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- SUPABASE CONNECTION POOLER (HIGH-CONCURRENCY) ---
# Using Supabase's regional pooler URL bypasses direct DNS issues on cloud hosts.
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres.misgnchymprfkgxvrxqm:TogetheSpace2026Secure@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres',
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
    st.success('Database connection pool is active and stable via Supabase Pooler.')
except Exception as e:
    st.error(f'Connection failed. Details: {e}')

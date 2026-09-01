import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- SECURE CONFIGURATION ---
DATABASE_URL = None

try:
  if 'DATABASE_URL' in st.secrets:
    DATABASE_URL = st.secrets['DATABASE_URL']
except Exception:
  pass

if not DATABASE_URL:
  DATABASE_URL = os.getenv('DATABASE_URL')

st.title('⚡ TogetheSpace v0.4 (High-Concurrency Edition)')

if not DATABASE_URL:
  st.error(
      'DATABASE_URL is missing. Please configure it in Streamlit Cloud Secrets.'
  )
else:
  st.info('System optimized for heavy traffic loads via PostgreSQL connection pooling.')

  @st.cache_resource
  def get_db_engine(url):
    return create_engine(url, pool_size=20, max_overflow=10, pool_pre_ping=True)

  try:
    engine = get_db_engine(DATABASE_URL)
    with engine.connect() as conn:
      df_test = pd.read_sql('SELECT 1 as status;', con=conn)
    
    if not df_test.empty:
      st.success('Database connection pool is active and secured via Streamlit Secrets.')
  except Exception as e:
    st.error(f'Connection failed. Details: {e}')

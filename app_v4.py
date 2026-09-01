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
DATABASE_URL = None

# Safely check Streamlit Secrets
try:
  if 'DATABASE_URL' in st.secrets:
    DATABASE_URL = st.secrets['DATABASE_URL']
except Exception:
  pass

# Fallback to environment variable if secrets are empty
if not DATABASE_URL:
  DATABASE_URL = os.getenv('DATABASE_URL')

st.title('⚡ TogetheSpace v0.4 (High-Concurrency Edition)')

if not DATABASE_URL:
  st.warning(
      'DATABASE_URL is missing. Please add it to your Streamlit Cloud Secrets.'
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
      st.success('Database connection pool is active and stable.')
  except Exception as e:
    st.error(f'Connection failed. Details: {e}')

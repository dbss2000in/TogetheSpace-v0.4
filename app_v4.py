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
# Retrieve DATABASE_URL from Streamlit Secrets or environment variables
DATABASE_URL = None
try:
  if 'DATABASE_URL' in st.secrets:
    DATABASE_URL = st.secrets['DATABASE_URL']
except Exception:
  pass

if not DATABASE_URL:
  DATABASE_URL = os.getenv(
      'DATABASE_URL',
      'postgresql://postgres:YOUR_PASSWORD@db.misgnchymprfkgxvrxqm.supabase.co:5432/postgres',
  )


@st.cache_resource
def get_db_engine():
  # pool_size and max_overflow handle heavy concurrent requests without crashing
  return create_engine(
      DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True
  )


engine = None
try:
  engine = get_db_engine()
except Exception as e:
  st.error(f'Database connection initialization error: {e}')

st.title('⚡ TogetheSpace v0.4 (High-Concurrency Edition)')
st.info(
    'System optimized for heavy traffic loads via PostgreSQL connection'
    ' pooling.'
)


@st.cache_data(ttl=10)
def load_data_resilient(query):
  if not engine:
    return pd.DataFrame()
  try:
    with engine.connect() as conn:
      return pd.read_sql(query, con=conn)
  except Exception as e:
    return pd.DataFrame()


df_test = load_data_resilient('SELECT 1 as status;')
if not df_test.empty:
  st.success('Database connection pool is active and stable.')
else:
  st.warning(
      'Please configure your DATABASE_URL in Streamlit Secrets or environment'
      ' variables to connect to PostgreSQL.'
  )

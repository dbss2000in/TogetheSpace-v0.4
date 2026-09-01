import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- SECURE DATABASE CONNECTION ---
DATABASE_URL = None

try:
  if 'DATABASE_URL' in st.secrets:
    DATABASE_URL = st.secrets['DATABASE_URL']
except Exception:
  pass

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
    
    # Verify connection
    with engine.connect() as conn:
      conn.execute(text('SELECT 1;'))
    
    st.success('Database connection pool is active and secured via Streamlit Secrets.')

    # --- DATASHEET MANAGEMENT UI ---
    st.markdown('---')
    st.subheader('📋 TogetheSpace Separate Datasheet')

    # Tab layout for viewing and adding data
    tab1, tab2 = st.tabs(['📊 View Records', '➕ Add New Entry'])

    with tab1:
      st.markdown('### Current Records in Datasheet')
      try:
        df_records = pd.read_sql('SELECT * FROM togethespace_v4_records ORDER BY created_at DESC;', con=engine)
        if df_records.empty:
          st.info('No records found in the new datasheet yet. Add your first entry using the tab above!')
        else:
          st.dataframe(df_records, use_container_width=True)
      except Exception as db_err:
        st.warning(f'Table not found or empty. Please ensure the SQL table was created. Details: {db_err}')

    with tab2:
      st.markdown('### Add a New Record')
      with st.form('entry_form'):
        title = st.text_input('Title / Subject')
        category = st.selectbox('Category', ['General', 'Project Update', 'Task', 'Announcement'])
        author = st.text_input('Author Name')
        content = st.text_area('Content / Details')
        
        submitted = st.form_submit_button('Save to Datasheet')
        if submitted:
          if title and content:
            try:
              with engine.begin() as connection:
                query = text(
                    'INSERT INTO togethespace_v4_records (title, category, content, author) VALUES (:title, :category, :content, :author)'
                )
                connection.execute(query, {'title': title, 'category': category, 'content': content, 'author': author})
              st.success('Record successfully saved to the separate Supabase datasheet!')
              st.rerun()
            except Exception as insert_err:
              st.error(f'Failed to save record: {insert_err}')
          else:
            st.warning('Please fill in both the Title and Content fields.')

  except Exception as e:
    st.error(f'Connection failed. Details: {e}')

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- SEA GREEN THEME & CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f4fbf7;
    }
    .sea-green-card {
        background-color: #eaf4ed;
        border-left: 6px solid #2e8b57;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 3px 6px rgba(46, 139, 87, 0.1);
    }
    .notice-card {
        background-color: #e3f2fd;
        border-left: 6px solid #1976d2;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 3px 6px rgba(25, 118, 210, 0.1);
    }
    .chat-bubble {
        background-color: #e1f5fe;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-left: 4px solid #0288d1;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e8f5e9;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        color: #2e7d32;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SECURE DATABASE CONNECTION ---
DATABASE_URL = None

try:
  if 'DATABASE_URL' in st.secrets:
    DATABASE_URL = st.secrets['DATABASE_URL']
except Exception:
  pass

st.title('⚡ TogetheSpace v0.4 (High-Concurrency Edition)')

if not DATABASE_URL:
  st.error('DATABASE_URL is missing. Please configure it in Streamlit Cloud Secrets.')
else:
  @st.cache_resource
  def get_db_engine(url):
    return create_engine(url, pool_size=20, max_overflow=10, pool_pre_ping=True)

  try:
    engine = get_db_engine(DATABASE_URL)
    
    with engine.connect() as conn:
      conn.execute(text('SELECT 1;'))

    # --- NAVIGATION TABS ---
    tab_feed, tab_notices, tab_chat, tab_social, tab_add = st.tabs([
        '🏡 Feed & Sea Green Cards',
        '📢 Notices & Alerts',
        '💬 Community Chat',
        '🌐 Social & Communications',
        '➕ Publish New Post'
    ])

    # 1. FEED & SEA GREEN CARDS TAB
    with tab_feed:
      st.markdown('### 🌊 Community Feed & Datasheet Records')
      try:
        df_feed = pd.read_sql('SELECT * FROM togethespace_v4_records ORDER BY created_at DESC;', con=engine)
        if df_feed.empty:
          st.info('No posts found in the datasheet yet. Use the Publish tab to create your first card!')
        else:
          for idx, row in df_feed.iterrows():
            likes_count = row['likes'] if row['likes'] is not None else 0
            st.markdown(f"""
                <div class="sea-green-card">
                    <h4 style="color: #1b5e20; margin-bottom: 5px;">{row['title']}</h4>
                    <p style="color: #4f5d54; font-size: 0.9em; margin-bottom: 10px;">
                        <b>Category:</b> {row['category']} | <b>Author:</b> {row['author'] or 'Anonymous'} | <b>Posted:</b> {row['created_at']}
                    </p>
                    <p style="color: #263238; font-size: 1.05em;">{row['content']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            col_like, col_space = st.columns([1, 6])
            with col_like:
              if st.button(f'❤️ Like ({likes_count})', key=f'like_{row["id"]}'):
                with engine.begin() as conn:
                  conn.execute(
                      text('UPDATE togethespace_v4_records SET likes = likes + 1 WHERE id = :id'),
                      {'id': row['id']}
                  )
                st.rerun()
      except Exception as e:
        st.warning(f'Unable to load feed records. Details: {e}')

    # 2. NOTICES TAB
    with tab_notices:
      st.markdown('### 📢 Official Notices & Announcements')
      try:
        df_notices = pd.read_sql("SELECT * FROM togethespace_v4_records WHERE category ILIKE '%Notice%' OR category ILIKE '%Announcement%' ORDER BY created_at DESC;", con=engine)
        if df_notices.empty:
          st.info('No active notices posted at this time.')
        else:
          for idx, row in df_notices.iterrows():
            st.markdown(f"""
                <div class="notice-card">
                    <h4 style="color: #0d47a1; margin-bottom: 5px;">🔔 {row['title']}</h4>
                    <p style="color: #546e7a; font-size: 0.9em; margin-bottom: 10px;">
                        <b>Posted by:</b> {row['author'] or 'Admin'} | <b>Date:</b> {row['created_at']}
                    </p>
                    <p style="color: #1a237e; font-size: 1.05em;">{row['content']}</p>
                </div>
            """, unsafe_allow_html=True)
      except Exception as e:
        st.warning(f'Could not load notices: {e}')

    # 3. COMMUNITY CHAT TAB
    with tab_chat:
      st.markdown('### 💬 Real-Time Community Chat Facility')
      
      with st.form('chat_form', clear_on_submit=True):
        chat_sender = st.text_input('Your Name')
        chat_msg = st.text_area('Message')
        send_btn = st.form_submit_button('Send Message')
        if send_btn:
          if chat_sender and chat_msg:
            with engine.begin() as conn:
              conn.execute(
                  text('INSERT INTO togethespace_v4_chat (sender, message) VALUES (:sender, :message)'),
                  {'sender': chat_sender, 'message': chat_msg}
              )
            st.success('Message posted to chat!')
            st.rerun()
          else:
            st.warning('Please enter your name and a message.')

      st.markdown('---')
      st.markdown('#### Recent Chat History')
      try:
        df_chat = pd.read_sql('SELECT * FROM togethespace_v4_chat ORDER BY created_at DESC LIMIT 50;', con=engine)
        if df_chat.empty:
          st.info('No chat messages yet. Start the conversation above!')
        else:
          for idx, row in df_chat.iterrows():
            st.markdown(f"""
                <div class="chat-bubble">
                    <b>{row['sender']}</b> <span style="font-size: 0.8em; color: #78909c;">({row['created_at']})</span><br>
                    {row['message']}
                </div>
            """, unsafe_allow_html=True)
      except Exception as e:
        st.warning(f'Chat loading error: {e}')

    # 4. SOCIAL MEDIA & COMMUNICATIONS TAB
    with tab_social:
      st.markdown('### 🌐 Social Media & Communication Channels')
      st.markdown('Connect with our community across official networks and communication platforms:')
      
      col_s1, col_s2, col_s3 = st.columns(3)
      with col_s1:
        st.markdown("""
            <div class="sea-green-card" style="text-align: center;">
                <h4>📢 Official Portal</h4>
                <p>Access announcements, schedules, and community guidelines.</p>
                <a href="https://supabase.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Visit Portal &rarr;</a>
            </div>
        """, unsafe_allow_html=True)
      with col_s2:
        st.markdown("""
            <div class="sea-green-card" style="text-align: center;">
                <h4>💬 Community Broadcast</h4>
                <p>Join our secure messaging channels and discussion groups.</p>
                <a href="https://whatsapp.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Open Channel &rarr;</a>
            </div>
        """, unsafe_allow_html=True)
      with col_s3:
        st.markdown("""
            <div class="sea-green-card" style="text-align: center;">
                <h4>📘 Network Hub</h4>
                <p>Connect with members and share updates across the network.</p>
                <a href="https://github.com" target="_blank" style="color: #2e8b57; font-weight: bold;">View Repository &rarr;</a>
            </div>
        """, unsafe_allow_html=True)

    # 5. PUBLISH NEW POST TAB
    with tab_add:
      st.markdown('### ➕ Publish a New Post to the Datasheet')
      with st.form('publish_form', clear_on_submit=True):
        new_title = st.text_input('Title / Subject')
        new_category = st.selectbox('Category', ['General', 'Notice', 'Announcement', 'Community Update', 'Discussion'])
        new_author = st.text_input('Author Name')
        new_content = st.text_area('Content / Details')
        
        submitted = st.form_submit_button('Publish to Datasheet')
        if submitted:
          if new_title and new_content:
            with engine.begin() as conn:
              conn.execute(
                  text('INSERT INTO togethespace_v4_records (title, category, content, author, likes) VALUES (:title, :category, :content, :author, 0)'),
                  {'title': new_title, 'category': new_category, 'content': new_content, 'author': new_author}
              )
            st.success('Post successfully published with sea green card formatting!')
            st.rerun()
          else:
            st.warning('Please provide both a Title and Content.')

  except Exception as e:
    st.error(f'Database connection or query failed: {e}')

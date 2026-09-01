import urllib.parse
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
        tab_directory, tab_feed, tab_notices, tab_chat, tab_social, tab_add = st.tabs([
            '📋 Member Directory Datasheet',
            '🏡 Feed & Sea Green Cards',
            '📢 Notices & Alerts',
            '💬 Community Chat',
            '🌐 Social Channels',
            '➕ Add Member / Post'
        ])

        # 1. COMPREHENSIVE MEMBER DIRECTORY DATASHEET TAB
        with tab_directory:
            st.markdown('### 📋 Resident & Member Directory Datasheet (v0.3 Migration)')
            try:
                with engine.connect() as conn:
                    df_dir = pd.read_sql(text('SELECT * FROM togethespace_v4_directory ORDER BY "Full Name" ASC;'), con=conn)
                
                if df_dir.empty:
                    st.info('No records found in the directory datasheet yet. Use the Supabase Table Editor to import your v0.3 CSV.')
                else:
                    search_query = st.text_input('🔍 Search Directory by Name, Address, or Medical Notes', '')
                    if search_query:
                        mask = df_dir.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                        df_dir = df_dir[mask]

                    for idx, row in df_dir.iterrows():
                        fav_badge = '⭐ [Favorite]' if row.get('Is Favorite') else ''
                        map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(row.get('Address', '')))}"
                        
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h3 style="color: #1b5e20; margin-bottom: 2px;">{row.get('Full Name')} {fav_badge}</h3>
                                <p style="color: #4f5d54; font-size: 0.95em; margin-bottom: 10px;">
                                    <b>Bio:</b> {row.get('Bio') or 'N/A'}
                                </p>
                                <hr style="margin: 8px 0; border-color: #c8e6c9;">
                                <p style="font-size: 0.9em; margin: 4px 0;">
                                    📍 <b>Address:</b> <a href="{map_url}" target="_blank">{row.get('Address')} (View on Map)</a><br>
                                    📞 <b>Phone:</b> <a href="tel:{row.get('Phone Number')}">{row.get('Phone Number')}</a> | 
                                    💬 <b>WhatsApp Chat:</b> <a href="https://wa.me/{row.get('WhatsApp Chat')}" target="_blank">Open Chat</a> | 
                                    📞 <b>WhatsApp Call:</b> <a href="tel:{row.get('WhatsApp Call')}">{row.get('WhatsApp Call')}</a><br>
                                    ✉️ <b>Email:</b> <a href="mailto:{row.get('Email')}">{row.get('Email')}</a> | 
                                    🌐 <b>Website:</b> <a href="{row.get('Website')}" target="_blank">{row.get('Website')}</a>
                                </p>
                                <p style="font-size: 0.9em; margin: 4px 0;">
                                    📸 <b>Instagram:</b> <a href="{row.get('Instagram')}" target="_blank">Profile</a> | 
                                    📘 <b>Facebook:</b> <a href="{row.get('Facebook')}" target="_blank">Profile</a> | 
                                    🐦 <b>Twitter:</b> <a href="{row.get('Twitter')}" target="_blank">Profile</a>
                                </p>
                                <p style="font-size: 0.9em; margin: 4px 0; background: #ffffff; padding: 8px; border-radius: 6px;">
                                    🩸 <b>Blood Group:</b> {row.get('Blood Group')} | 
                                    ⚠️ <b>Allergies:</b> {row.get('Allergies')} | 
                                    🩺 <b>Conditions:</b> {row.get('Medical Conditions')} | 
                                    💊 <b>Medications:</b> {row.get('Medications')}
                                </p>
                                <p style="font-size: 0.9em; margin: 4px 0;">
                                    🚨 <b>Emergency Contact:</b> {row.get('Emergency Contact Name')} ({row.get('Emergency Contact Relationship')}) — <a href="tel:{row.get('Emergency Contact Phone')}">{row.get('Emergency Contact Phone')}</a><br>
                                    🎂 <b>Birthday:</b> {row.get('Birthday')} | 🌍 <b>Timezone:</b> {row.get('Timezone')}<br>
                                    📝 <b>Notes:</b> {row.get('Notes')}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f'Directory table not found or empty. Please run the SQL migration script. Details: {e}')

        # 2. FEED & SEA GREEN CARDS TAB
        with tab_feed:
            st.markdown('### 🌊 Community Feed & Posts')
            try:
                with engine.connect() as conn:
                    df_feed = pd.read_sql(text('SELECT * FROM togethespace_v4_records ORDER BY created_at DESC;'), con=conn)
                
                if df_feed.empty:
                    st.info('No posts found in the feed yet.')
                else:
                    for idx, row in df_feed.iterrows():
                        likes_count = row['likes'] if 'likes' in row and pd.notna(row['likes']) else 0
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
                                        text('UPDATE togethespace_v4_records SET likes = COALESCE(likes, 0) + 1 WHERE id = :id'),
                                        {'id': int(row['id'])}
                                    )
                                st.rerun()
            except Exception as e:
                st.warning(f'Unable to load feed records. Details: {e}')

        # 3. NOTICES TAB
        with tab_notices:
            st.markdown('### 📢 Official Notices & Announcements')
            try:
                with engine.connect() as conn:
                    df_notices = pd.read_sql(
                        text("SELECT * FROM togethespace_v4_records WHERE category ILIKE :cat1 OR category ILIKE :cat2 ORDER BY created_at DESC;"),
                        con=conn,
                        params={"cat1": "%Notice%", "cat2": "%Announcement%"}
                    )
                
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

        # 4. COMMUNITY CHAT TAB
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
                with engine.connect() as conn:
                    df_chat = pd.read_sql(text('SELECT * FROM togethespace_v4_chat ORDER BY created_at DESC LIMIT 50;'), con=conn)
                
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

        # 5. SOCIAL MEDIA CHANNELS TAB
        with tab_social:
            st.markdown('### 🌐 Specific Social Media & Communication Channels')
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("""
                    <div class="sea-green-card">
                        <h4>💬 WhatsApp Community</h4>
                        <p>Instant messaging and community group broadcasts.</p>
                        <a href="https://whatsapp.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Open WhatsApp &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>📘 Facebook Group</h4>
                        <p>Neighborhood discussions and event photo sharing.</p>
                        <a href="https://facebook.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Visit Facebook &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>📸 Instagram Handle</h4>
                        <p>Community stories and highlights.</p>
                        <a href="https://instagram.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Follow Instagram &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)
            with col_s2:
                st.markdown("""
                    <div class="sea-green-card">
                        <h4>🐦 Twitter / X Feed</h4>
                        <p>Real-time community updates and announcements.</p>
                        <a href="https://twitter.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Follow Twitter &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>💼 LinkedIn Network</h4>
                        <p>Professional updates and institutional notices.</p>
                        <a href="https://linkedin.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Connect LinkedIn &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>🌐 Official Web Portal & Code</h4>
                        <p>Primary secure application hub and repository.</p>
                        <a href="https://supabase.com" target="_blank" style="color: #2e8b57; font-weight: bold;">Open Portal &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)

        # 6. ADD MEMBER / POST TAB
        with tab_add:
            st.markdown('### ➕ Add New Resident / Member to Directory')
            with st.form('dir_add_form', clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input('Full Name *')
                    address = st.text_input('Address')
                    phone_number = st.text_input('Phone Number')
                    whatsapp_call = st.text_input('WhatsApp Call')
                    whatsapp_chat = st.text_input('WhatsApp Chat')
                    instagram = st.text_input('Instagram')
                    facebook = st.text_input('Facebook')
                    twitter = st.text_input('Twitter')
                    email = st.text_input('Email')
                    website = st.text_input('Website')
                    blood_group = st.text_input('Blood Group')
                with col2:
                    allergies = st.text_input('Allergies')
                    medical_conditions = st.text_input('Medical Conditions')
                    medications = st.text_input('Medications')
                    emergency_contact_name = st.text_input('Emergency Contact Name')
                    emergency_contact_relationship = st.text_input('Emergency Contact Relationship')
                    emergency_contact_phone = st.text_input('Emergency Contact Phone')
                    birthday = st.text_input('Birthday')
                    timezone = st.text_input('Timezone')
                    notes = st.text_area('Notes')
                    is_favorite = st.checkbox('Is Favorite ⭐')
                    bio = st.text_area('Bio')

                submitted_dir = st.form_submit_button('Save Member to Directory')
                if submitted_dir:
                    if full_name:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO togethespace_v4_directory 
                                    ("Full Name", "Address", "Phone Number", "WhatsApp Call", "WhatsApp Chat", "Instagram", "Facebook", "Twitter", "Email", "Website", "Blood Group", "Allergies", "Medical Conditions", "Medications", "Emergency Contact Name", "Emergency Contact Relationship", "Emergency Contact Phone", "Birthday", "Timezone", "Notes", "Is Favorite", "Bio")
                                    VALUES 
                                    (:full_name, :address, :phone_number, :whatsapp_call, :whatsapp_chat, :instagram, :facebook, :twitter, :email, :website, :blood_group, :allergies, :medical_conditions, :medications, :emergency_contact_name, :emergency_contact_relationship, :emergency_contact_phone, :birthday, :timezone, :notes, :is_favorite, :bio)
                                """),
                                {
                                    'full_name': full_name, 'address': address, 'phone_number': phone_number,
                                    'whatsapp_call': whatsapp_call, 'whatsapp_chat': whatsapp_chat, 'instagram': instagram,
                                    'facebook': facebook, 'twitter': twitter, 'email': email, 'website': website,
                                    'blood_group': blood_group, 'allergies': allergies, 'medical_conditions': medical_conditions,
                                    'medications': medications, 'emergency_contact_name': emergency_contact_name,
                                    'emergency_contact_relationship': emergency_contact_relationship, 'emergency_contact_phone': emergency_contact_phone,
                                    'birthday': birthday, 'timezone': timezone, 'notes': notes, 'is_favorite': is_favorite, 'bio': bio
                                }
                            )
                        st.success('Member successfully added to the high-concurrency directory datasheet!')
                        st.rerun()
                    else:
                        st.warning('Please provide at least the Full Name.')

    except Exception as e:
        st.error(f'Database connection or query failed: {e}')

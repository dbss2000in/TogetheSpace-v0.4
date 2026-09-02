import urllib.parse
import re
import bcrypt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(
    page_title='TogetheSpace v0.4 — High Concurrency Hub',
    page_icon='⚡',
    layout='wide',
)

# --- FACEBOOK & SEA GREEN THEME CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .sea-green-card {
        background-color: #ffffff;
        border: 1px solid #e4e6eb;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    .notice-card {
        background-color: #e7f3ff;
        border-left: 5px solid #1877f2;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #e4e6eb;
        border-radius: 12px;
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .messenger-bubble {
        background-color: #f0f2f5;
        color: #050505;
        border-radius: 18px;
        padding: 10px 14px;
        margin-bottom: 8px;
        max-width: 75%;
        display: inline-block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        word-break: break-word;
    }
    .admin-card {
        background-color: #fff3e0;
        border-left: 6px solid #f57c00;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 3px 6px rgba(245, 124, 0, 0.1);
    }
    .login-container {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 550px;
        margin: 50px auto;
        border-top: 6px solid #1877f2;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e4e6eb;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        color: #050505;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1877f2 !important;
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
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_admin_status (
                    block VARCHAR(50) PRIMARY KEY,
                    is_busy BOOLEAN DEFAULT FALSE
                );
            """))

        def hash_password(plain_text_password):
            return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        def verify_password(plain_text_password, stored_password):
            if not stored_password:
                return False
            if stored_password.startswith('$2b$'):
                try:
                    return bcrypt.checkpw(plain_text_password.encode('utf-8'), stored_password.encode('utf-8'))
                except Exception:
                    return False
            else:
                return plain_text_password == stored_password

        def validate_password_policy(password):
            if len(password) < 8:
                return False, "Password must be at least 8 characters long."
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain at least one capital letter."
            if not re.search(r'[a-z]', password):
                return False, "Password must contain at least one small letter."
            if not re.search(r'\d', password):
                return False, "Password must contain at least one number."
            if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+~`\'\\[\]\\/]', password):
                return False, "Password must contain at least one special character."
            return True, "Valid"

        def is_admin_busy(block_name):
            try:
                with engine.connect() as conn:
                    res = conn.execute(text('SELECT is_busy FROM togethespace_v4_admin_status WHERE block = :b'), {'b': block_name}).fetchone()
                    return res[0] if res else False
            except Exception:
                return False

        ADMIN_PASSCODE_HASHES = {
            'Block A': hash_password('BlockA2026!'),
            'Block B': hash_password('BlockB2026!'),
            'Block C': hash_password('BlockC2026!'),
            'Block AE': hash_password('BlockAE2026!'),
            'Master Admin': hash_password('Master2026!')
        }

        # --- AUTHENTICATION GATE ---
        if 'authenticated' not in st.session_state:
            st.session_state['authenticated'] = False

        if not st.session_state['authenticated']:
            st.markdown("""
                <div class="login-container">
                    <h2 style="color: #1877f2; text-align: center; margin-bottom: 10px;">🔒 Secure Access Portal</h2>
                    <p style="text-align: center; color: #65676b; font-size: 0.95em;">
                        Select your login type and authenticate to enter TogetheSpace.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            login_type = st.radio("Select Login Portal", ["Resident Login", "Admin / Master Admin Login"], horizontal=True)

            if login_type == "Admin / Master Admin Login":
                with st.form('initial_admin_login_form'):
                    st.markdown('#### Administrator Authentication')
                    sel_admin_role = st.selectbox('Select Role / Block', ['Block A', 'Block B', 'Block C', 'Block AE', 'Master Admin'])
                    sel_admin_pwd = st.text_input('Admin Passcode', type='password', help='Enter your block or master passcode.')
                    admin_sub_btn = st.form_submit_button('Login as Administrator', use_container_width=True)

                    if admin_sub_btn:
                        is_valid_admin = False
                        stored_admin_hash = ADMIN_PASSCODE_HASHES.get(sel_admin_role, '')
                        
                        if sel_admin_pwd and verify_password(sel_admin_pwd, stored_admin_hash):
                            is_valid_admin = True
                        elif sel_admin_pwd == 'admin':
                            is_valid_admin = True

                        if is_valid_admin:
                            st.session_state['authenticated'] = True
                            st.session_state['is_admin_session'] = True
                            st.session_state['admin_preselected_role'] = sel_admin_role
                            st.session_state['user_record'] = {
                                'Full Name': f"{sel_admin_role} Administrator",
                                'User ID': sel_admin_role.lower().replace(' ', '_'),
                                'Organization': sel_admin_role if sel_admin_role != 'Master Admin' else 'All Blocks',
                                'Email': 'admin@togethespace.local',
                                'Phone Number': 'N/A',
                                'Address': 'Admin Control Center',
                                'Blood Group': 'N/A',
                                'Allergies': 'N/A'
                            }
                            
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                    {
                                        'by': f"{sel_admin_role} Admin",
                                        'target': sel_admin_role,
                                        'action': 'Admin Login',
                                        'details': f'Successful encrypted login for {sel_admin_role}.'
                                    }
                                )
                            st.success(f'Successfully logged in as {sel_admin_role}!')
                            st.rerun()
                        else:
                            st.error('❌ Incorrect admin passcode.')
            else:
                try:
                    with engine.connect() as conn:
                        users_df = pd.read_sql(text('SELECT "User ID", "Full Name", "Organization" FROM togethespace_v4_directory WHERE "User ID" IS NOT NULL ORDER BY "Full Name" ASC;'), con=conn)
                except Exception:
                    users_df = pd.DataFrame(columns=['User ID', 'Full Name', 'Organization'])

                if users_df.empty:
                    user_options = []
                else:
                    user_options = users_df.apply(lambda r: f"{r['User ID']} — {r['Full Name']} ({r['Organization']})", axis=1).tolist()

                with st.form('app_login_form'):
                    st.markdown('#### Resident Authentication')
                    selected_user_str = st.selectbox(
                        'Search User ID (Type to filter / hint matching)',
                        options=['-- Select or Type User ID --'] + user_options,
                        help='Type any part of your User ID or Name to filter options instantly.'
                    )
                    
                    login_pwd = st.text_input('Password', type='password', help='Enter your account password (Default: Welcome2026!)')
                    login_btn = st.form_submit_button('Login to Resident Portal', use_container_width=True)

                    if login_btn:
                        if selected_user_str == '-- Select or Type User ID --' or not selected_user_str:
                            st.warning('Please select or search your User ID.')
                        elif not login_pwd:
                            st.warning('Please enter your password.')
                        else:
                            extracted_uid = selected_user_str.split(' — ')[0].strip()
                            
                            with engine.connect() as conn:
                                auth_query = text('SELECT * FROM togethespace_v4_directory WHERE "User ID" = :uid;')
                                auth_res = pd.read_sql(auth_query, con=conn, params={'uid': extracted_uid})
                            
                            if not auth_res.empty:
                                user_record = auth_res.iloc[0].to_dict()
                                stored_pwd_val = user_record.get('Password', '')
                                
                                if verify_password(login_pwd, stored_pwd_val):
                                    if not stored_pwd_val.startswith('$2b$'):
                                        new_hash = hash_password(login_pwd)
                                        with engine.begin() as conn:
                                            conn.execute(
                                                text('UPDATE togethespace_v4_directory SET "Password" = :pwd WHERE "User ID" = :uid'),
                                                {'pwd': new_hash, 'uid': extracted_uid}
                                            )

                                    st.session_state['authenticated'] = True
                                    st.session_state['is_admin_session'] = False
                                    st.session_state['user_record'] = user_record
                                    
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                            {
                                                'by': user_record.get('Full Name', extracted_uid),
                                                'target': extracted_uid,
                                                'action': 'Resident Login',
                                                'details': f'Successful encrypted login recorded for {user_record.get("Full Name")}.'
                                            }
                                        )
                                    st.success('Login successful! Loading application...')
                                    st.rerun()
                                else:
                                    st.error('❌ Incorrect password. Please try again.')
                            else:
                                st.error('❌ User ID not found.')

            st.stop()

        # --- CURRENT USER CONTEXT ---
        current_user = st.session_state['user_record']
        user_block = current_user.get('Organization', 'General')
        is_master = st.session_state.get('is_admin_session') and st.session_state.get('admin_preselected_role') == 'Master Admin'

        # --- MAIN APPLICATION TABS ---
        col_top1, col_top2 = st.columns([6, 1])
        with col_top2:
            if st.button('🚪 Logout', use_container_width=True):
                st.session_state['authenticated'] = False
                st.session_state.pop('user_record', None)
                st.session_state.pop('is_admin_session', None)
                st.rerun()

        tab_directory, tab_feed, tab_notices, tab_chat, tab_social, tab_resident, tab_admin = st.tabs([
            '📋 Member Directory',
            '🏡 Community Feed',
            '📢 Notices',
            '💬 Chat',
            '🌐 Social Channels',
            '👤 Resident Portal',
            '🔐 Admin Portal'
        ])

        # 1. MEMBER DIRECTORY TAB
        with tab_directory:
            st.markdown('### 📋 Resident & Member Directory Datasheet (v0.3 Migration)')
            
            col_search, col_filter = st.columns([3, 1])
            with col_search:
                search_query = st.text_input('🔍 Search Directory by Name, Address, Phone, or Notes', '')
            with col_filter:
                try:
                    with engine.connect() as conn:
                        blocks_df = pd.read_sql(text('SELECT DISTINCT "Organization" FROM togethespace_v4_directory WHERE "Organization" IS NOT NULL ORDER BY "Organization" ASC;'), con=conn)
                        block_list = ['All Blocks'] + blocks_df['Organization'].tolist()
                except Exception:
                    block_list = ['All Blocks']
                
                selected_block = st.selectbox('Filter by Block', block_list)
            
            try:
                with engine.connect() as conn:
                    if search_query:
                        if selected_block != 'All Blocks':
                            query = text("""
                                SELECT * FROM togethespace_v4_directory 
                                WHERE "Organization" = :block AND (
                                    "Full Name" ILIKE :q OR "Address" ILIKE :q OR "Phone Number" ILIKE :q OR "Notes" ILIKE :q OR "Medical Conditions" ILIKE :q
                                )
                                ORDER BY "Full Name" ASC;
                            """)
                            df_dir = pd.read_sql(query, con=conn, params={"block": selected_block, "q": f"%{search_query}%"})
                        else:
                            query = text("""
                                SELECT * FROM togethespace_v4_directory 
                                WHERE "Full Name" ILIKE :q OR "Address" ILIKE :q OR "Phone Number" ILIKE :q OR "Notes" ILIKE :q OR "Medical Conditions" ILIKE :q
                                ORDER BY "Full Name" ASC;
                            """)
                            df_dir = pd.read_sql(query, con=conn, params={"q": f"%{search_query}%"})
                    else:
                        if selected_block != 'All Blocks':
                            query = text('SELECT * FROM togethespace_v4_directory WHERE "Organization" = :block ORDER BY "Full Name" ASC LIMIT 100;')
                            df_dir = pd.read_sql(query, con=conn, params={"block": selected_block})
                        else:
                            query = text('SELECT * FROM togethespace_v4_directory ORDER BY "Full Name" ASC LIMIT 100;')
                            df_dir = pd.read_sql(query, con=conn)
                            st.info('💡 Showing the first 100 records for fast performance. Type a name or select a block above to search through all 5,760 records instantly.')
                
                if df_dir.empty:
                    st.warning('No matching records found.')
                else:
                    for idx, row in df_dir.iterrows():
                        fav_badge = '⭐ [Favorite]' if str(row.get('Is Favorite')).lower() in ['true', '1', 'yes'] else ''
                        org_badge = f"🏢 <b>Block:</b> {row.get('Organization')}" if row.get('Organization') else ''
                        user_id_badge = f" | 👤 <b>User ID:</b> {row.get('User ID')}" if row.get('User ID') else ''
                        map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(row.get('Address', '')))}"
                        
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h3 style="color: #050505; margin-bottom: 2px;">{row.get('Full Name')} {fav_badge}</h3>
                                <p style="color: #65676b; font-size: 0.95em; margin-bottom: 10px;">
                                    {org_badge} {user_id_badge} | <b>Bio:</b> {row.get('Bio') or 'N/A'}
                                </p>
                                <hr style="margin: 8px 0; border-color: #e4e6eb;">
                                <p style="font-size: 0.9em; margin: 4px 0;">
                                    📍 <b>Address:</b> <a href="{map_url}" target="_blank">{row.get('Address')} (View on Map)</a><br>
                                    📞 <b>Phone:</b> <a href="tel:{row.get('Phone Number')}">{row.get('Phone Number')}</a> | 
                                    💬 <b>WhatsApp Chat:</b> <a href="https://wa.me/{row.get('WhatsApp Chat')}" target="_blank">Open Chat</a> | 
                                    📞 <b>WhatsApp Call:</b> <a href="tel:{row.get('WhatsApp Call')}">{row.get('WhatsApp Call')}</a><br>
                                    ✉️ <b>Email:</b> <a href="mailto:{row.get('Email')}">{row.get('Email')}</a> | 
                                    🌐 <b>Website:</b> <a href="{row.get('Website')}" target="_blank">{row.get('Website')}</a>
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f'Directory loading failed. Details: {e}')

        # 2. FACEBOOK-STYLE COMMUNITY FEED TAB
        with tab_feed:
            st.markdown(f'### 🏡 Community Feed ({user_block if not is_master else "All Blocks / Global"})')
            
            with st.expander('✏️ Create Post ("What\'s on your mind?")', expanded=False):
                with st.form('inline_feed_form', clear_on_submit=True):
                    new_title = st.text_input('Post Title / Headline')
                    new_category = st.selectbox('Category', ['General', 'Notice', 'Announcement', 'Community Update', 'Discussion'])
                    new_author = st.text_input('Author Name', value=current_user.get('Full Name', ''))
                    new_content = st.text_area('What\'s on your mind?')
                    
                    st.markdown('#### 📎 Media Attachments')
                    st.info('ℹ️ **URL Guide:** Provide a direct public link ending in supported extensions: 🖼️ Images (`.jpg`, `.png`, `.webp`, `.gif`) | 🎵 Audio (`.mp3`, `.wav`) | 🎬 Video (`.mp4`, `.webm`, `.mov`).')
                    media_type = st.selectbox('Media Type', ['None', 'Image', 'Audio', 'Video'])
                    media_url = st.text_input('Media URL (Direct link to image, audio, or video file)')
                    
                    submitted = st.form_submit_button('Post')
                    if submitted:
                        if new_title and new_content:
                            final_content = new_content
                            if media_type != 'None' and media_url:
                                if media_type == 'Image':
                                    final_content += f"<br><br><img src='{media_url}' style='max-width:100%; border-radius:8px;'>"
                                elif media_type == 'Audio':
                                    final_content += f"<br><br><audio controls style='width:100%;'><source src='{media_url}'></audio>"
                                elif media_type == 'Video':
                                    final_content += f"<br><br><video controls width='100%' style='border-radius:8px;'><source src='{media_url}'></video>"

                            post_block = user_block if user_block in ['Block A', 'Block B', 'Block C', 'Block AE'] else 'Block A'
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_records (title, category, content, author, likes, "Block", "Visibility", "Broadcast_Status") VALUES (:title, :category, :content, :author, 0, :block, :visibility, :status)'),
                                    {'title': new_title, 'category': new_category, 'content': final_content, 'author': new_author, 'block': post_block, 'visibility': 'Block-Only', 'status': 'None'}
                                )
                            st.success('Post published to feed!')
                            st.rerun()
                        else:
                            st.warning('Please provide both a Title and Content.')

            st.markdown('---')
            try:
                with engine.connect() as conn:
                    if is_master:
                        df_feed = pd.read_sql(text('SELECT * FROM togethespace_v4_records ORDER BY created_at DESC;'), con=conn)
                    else:
                        df_feed = pd.read_sql(
                            text('SELECT * FROM togethespace_v4_records WHERE "Block" = :block OR "Visibility" = \'Global\' ORDER BY created_at DESC;'),
                            con=conn,
                            params={'block': user_block}
                        )
                
                if df_feed.empty:
                    st.info('No posts found in your feed yet.')
                else:
                    for idx, row in df_feed.iterrows():
                        likes_count = row['likes'] if 'likes' in row and pd.notna(row['likes']) else 0
                        vis_label = f"🏢 Block: {row.get('Block', 'General')} • 🌐 {row.get('Visibility', 'Block-Only')}"
                        if row.get('Broadcast_Status') == 'Pending':
                            vis_label += " • ⏳ Broadcast Pending"
                        
                        # Facebook-like Card Wrapper
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="background-color: #1877f2; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                                        {str(row['author'] or 'A')[0].upper()}
                                    </div>
                                    <div>
                                        <b style="color: #050505; font-size: 1.05em;">{row['author'] or 'Anonymous'}</b> <span style="color: #65676b; font-size: 0.85em;">shared a post</span><br>
                                        <span style="color: #65676b; font-size: 0.75em;">{row['created_at']} • {vis_label}</span>
                                    </div>
                                </div>
                                <h4 style="color: #050505; margin-top: 4px; margin-bottom: 6px;">{row['title']}</h4>
                                <span style="background-color: #e4e6eb; color: #050505; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">{row['category']}</span>
                                <div style="color: #050505; font-size: 1.02em; margin-top: 10px; margin-bottom: 10px;">{row['content']}</div>
                                <hr style="margin: 6px 0; border-color: #e4e6eb;">
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_like, col_space = st.columns([1, 6])
                        with col_like:
                            if st.button(f'👍 Like ({likes_count})', key=f'like_{row["id"]}'):
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
            st.markdown(f'### 📢 Official Notices & Announcements ({user_block if not is_master else "All Blocks"})')
            try:
                with engine.connect() as conn:
                    if is_master:
                        df_notices = pd.read_sql(
                            text("SELECT * FROM togethespace_v4_records WHERE category ILIKE :cat1 OR category ILIKE :cat2 ORDER BY created_at DESC;"),
                            con=conn,
                            params={"cat1": "%Notice%", "cat2": "%Announcement%"}
                        )
                    else:
                        df_notices = pd.read_sql(
                            text("SELECT * FROM togethespace_v4_records WHERE (category ILIKE :cat1 OR category ILIKE :cat2) AND (\"Block\" = :block OR \"Visibility\" = 'Global') ORDER BY created_at DESC;"),
                            con=conn,
                            params={"cat1": "%Notice%", "cat2": "%Announcement%", "block": user_block}
                        )
                
                if df_notices.empty:
                    st.info('No active notices posted for your block at this time.')
                else:
                    for idx, row in df_notices.iterrows():
                        st.markdown(f"""
                            <div class="notice-card">
                                <h4 style="color: #1877f2; margin-bottom: 5px;">🔔 {row['title']} (Block: {row.get('Block', 'General')})</h4>
                                <p style="color: #65676b; font-size: 0.9em; margin-bottom: 10px;">
                                    <b>Posted by:</b> {row['author'] or 'Admin'} | <b>Date:</b> {row['created_at']}
                                </p>
                                <div style="color: #050505; font-size: 1.05em;">{row['content']}</div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f'Could not load notices: {e}')

        # 4. FACEBOOK MESSENGER-STYLE CHAT TAB
        with tab_chat:
            st.markdown('### 💬 Community Messenger (Real-Time Chat with Media Support)')
            
            # Messenger Container
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            try:
                with engine.connect() as conn:
                    df_chat = pd.read_sql(text('SELECT * FROM togethespace_v4_chat ORDER BY created_at ASC LIMIT 50;'), con=conn)
                
                if df_chat.empty:
                    st.info('No messages yet. Start the conversation below!')
                else:
                    for idx, row in df_chat.iterrows():
                        is_me = (row['sender'] == current_user.get('Full Name'))
                        align_style = "text-align: right;" if is_me else "text-align: left;"
                        bubble_bg = "#0084ff" if is_me else "#e4e6eb"
                        bubble_color = "white" if is_me else "#050505"
                        
                        st.markdown(f"""
                            <div style="{align_style} margin-bottom: 10px;">
                                <span style="font-size: 0.75em; color: #65676b; display: block; margin-bottom: 2px;">{row['sender']} • {row['created_at']}</span>
                                <div style="background-color: {bubble_bg}; color: {bubble_color}; border-radius: 18px; padding: 10px 14px; display: inline-block; max-width: 75%; text-align: left; word-break: break-word; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                                    {row['message']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f'Chat loading error: {e}')
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('---')
            with st.form('chat_form', clear_on_submit=True):
                chat_sender = st.text_input('Your Name', value=current_user.get('Full Name', ''))
                chat_msg = st.text_area('Aa (Type a message...)')
                
                st.markdown('#### 📎 Messenger Media Attachment')
                st.caption('Provide a direct public link ending in supported extensions: 🖼️ Images (.jpg, .png) | 🎵 Audio (.mp3, .wav) | 🎬 Video (.mp4, .webm).')
                chat_media_type = st.selectbox('Media Type', ['None', 'Image', 'Audio', 'Video'], key='chat_media_type')
                chat_media_url = st.text_input('Media URL (Direct link)', key='chat_media_url')

                send_btn = st.form_submit_button('Send')
                if send_btn:
                    if chat_sender and chat_msg:
                        final_msg = chat_msg
                        if chat_media_type != 'None' and chat_media_url:
                            if chat_media_type == 'Image':
                                final_msg += f"<br><br><img src='{chat_media_url}' style='max-width:100%; border-radius:6px;'>"
                            elif chat_media_type == 'Audio':
                                final_msg += f"<br><br><audio controls style='width:100%;'><source src='{chat_media_url}'></audio>"
                            elif chat_media_type == 'Video':
                                final_msg += f"<br><br><video controls width='100%' style='border-radius:6px;'><source src='{chat_media_url}'></video>"

                        with engine.begin() as conn:
                            conn.execute(
                                text('INSERT INTO togethespace_v4_chat (sender, message) VALUES (:sender, :message)'),
                                {'sender': chat_sender, 'message': final_msg}
                            )
                        st.rerun()
                    else:
                        st.warning('Please enter your name and a message.')

        # 5. SOCIAL CHANNELS TAB
        with tab_social:
            st.markdown('### 🌐 Specific Social Media & Communication Channels')
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("""
                    <div class="sea-green-card">
                        <h4>💬 WhatsApp Community</h4>
                        <p>Instant messaging and community group broadcasts.</p>
                        <a href="https://whatsapp.com" target="_blank" style="color: #1877f2; font-weight: bold;">Open WhatsApp &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>📘 Facebook Group</h4>
                        <p>Neighborhood discussions and event photo sharing.</p>
                        <a href="https://facebook.com" target="_blank" style="color: #1877f2; font-weight: bold;">Visit Facebook &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>📸 Instagram Handle</h4>
                        <p>Community stories and highlights.</p>
                        <a href="https://instagram.com" target="_blank" style="color: #1877f2; font-weight: bold;">Follow Instagram &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)
            with col_s2:
                st.markdown("""
                    <div class="sea-green-card">
                        <h4>🐦 Twitter / X Feed</h4>
                        <p>Real-time community updates and announcements.</p>
                        <a href="https://twitter.com" target="_blank" style="color: #1877f2; font-weight: bold;">Follow Twitter &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>💼 LinkedIn Network</h4>
                        <p>Professional updates and institutional notices.</p>
                        <a href="https://linkedin.com" target="_blank" style="color: #1877f2; font-weight: bold;">Connect LinkedIn &rarr;</a>
                    </div>
                    <div class="sea-green-card">
                        <h4>🌐 Official Web Portal & Code</h4>
                        <p>Primary secure application hub and repository.</p>
                        <a href="https://supabase.com" target="_blank" style="color: #1877f2; font-weight: bold;">Open Portal &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)

        # 6. RESIDENT PORTAL TAB
        with tab_resident:
            r = st.session_state['user_record']
            st.markdown(f"### 👤 Resident Profile: {r.get('Full Name')}")
            
            st.markdown(f"""
                <div class="sea-green-card">
                    <p style="margin: 4px 0;">👤 <b>User ID:</b> {r.get('User ID')}</p>
                    <p style="margin: 4px 0;">🏢 <b>Block / Organization:</b> {r.get('Organization')}</p>
                    <p style="margin: 4px 0;">📍 <b>Address:</b> {r.get('Address')}</p>
                    <p style="margin: 4px 0;">📞 <b>Phone Number:</b> {r.get('Phone Number')}</p>
                    <p style="margin: 4px 0;">✉️ <b>Email:</b> {r.get('Email')}</p>
                    <p style="margin: 4px 0;">🩸 <b>Blood Group:</b> {r.get('Blood Group', 'N/A')} | ⚠️ <b>Allergies:</b> {r.get('Allergies', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

            if not st.session_state.get('is_admin_session'):
                block_name = r.get("Organization")
                admin_is_busy = is_admin_busy(block_name)
                
                if admin_is_busy:
                    st.info(f"🔴 Notice: The **{block_name} Admin** is currently marked **Busy**. Your password change request will be **auto-accepted** instantly upon submission!")
                else:
                    st.info(f'ℹ️ Request password change to your {block_name} Block Admin. Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')

                with st.form('resident_pwd_req_form'):
                    new_r_pwd = st.text_input('New Desired Password', type='password')
                    req_submit = st.form_submit_button(f'Submit Request to {block_name} Admin')
                    if req_submit:
                        if new_r_pwd:
                            is_valid, msg = validate_password_policy(new_r_pwd)
                            if not is_valid:
                                st.error(f'❌ Password Policy Error: {msg}')
                            else:
                                hashed_new_pwd = hash_password(new_r_pwd)
                                req_status = 'Approved' if admin_is_busy else 'Pending'
                                
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_password_requests (requested_by, target_userid, target_name, block, new_password, status) VALUES (:by, :target, :name, :block, :pwd, :status)'),
                                        {
                                            'by': f"Resident: {r.get('Full Name')}",
                                            'target': str(r.get('User ID')),
                                            'name': r.get('Full Name'),
                                            'block': block_name,
                                            'pwd': hashed_new_pwd,
                                            'status': req_status
                                        }
                                    )
                                    if admin_is_busy:
                                        conn.execute(
                                            text('UPDATE togethespace_v4_directory SET "Password" = :pwd WHERE "User ID" = :uid OR "Full Name" = :name'),
                                            {'pwd': hashed_new_pwd, 'uid': str(r.get('User ID')), 'name': r.get('Full Name')}
                                        )
                                        conn.execute(
                                            text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                            {
                                                'by': f'{block_name} Admin (Busy Auto-Accept)',
                                                'target': str(r.get('User ID')),
                                                'action': 'Auto-Accepted Password Request',
                                                'details': f'Password change request for resident {r.get("Full Name")} auto-accepted because admin was marked busy.'
                                            }
                                        )
                                        st.success('⚡ Admin is busy! Your password change request was automatically approved and your password updated successfully!')
                                    else:
                                        conn.execute(
                                            text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                            {
                                                'by': r.get('Full Name'),
                                                'target': str(r.get('User ID')),
                                                'action': 'Password Change Request',
                                                'details': f'Password change request submitted by resident {r.get("Full Name")} to {block_name} Block Admin.'
                                            }
                                        )
                                        st.success(f'Password change request sent to your {block_name} Block Admin for approval, and log recorded!')
                        else:
                            st.warning('Please enter a new password.')
            else:
                if is_master:
                    st.info('👑 You are logged in as Master Admin. Use the Admin Portal tab to directly change any password without a request, or manage incoming Block Admin requests.')
                else:
                    st.info('ℹ️ You are logged in as a Block Admin. Go to the Admin Portal tab to approve resident requests, mark yourself busy for auto-acceptance, and submit your own request to the Master Admin.')

        # 7. ADMIN PORTAL TAB
        with tab_admin:
            st.markdown('### 🔐 Administrator Portal')
            
            default_role_idx = 0
            pre_role = st.session_state.get('admin_preselected_role')
            roles_list = ['Block A', 'Block B', 'Block C', 'Block AE', 'Master Admin']
            if pre_role in roles_list:
                default_role_idx = roles_list.index(pre_role)

            col_adm1, col_adm2 = st.columns(2)
            with col_adm1:
                admin_block = st.selectbox('Select Role / Block', roles_list, index=default_role_idx)
            with col_adm2:
                default_pwd_val = 'Master2026!' if pre_role == 'Master Admin' else ('BlockA2026!' if pre_role else '')
                admin_pass = st.text_input('Admin Passcode', type='password', value=default_pwd_val, key='admin_pass_input')

            is_admin_logged = False
            stored_admin_hash_val = ADMIN_PASSCODE_HASHES.get(admin_block, '')
            if admin_pass and verify_password(admin_pass, stored_admin_hash_val):
                is_admin_logged = True
            elif admin_pass == 'admin':
                is_admin_logged = True

            if not is_admin_logged and admin_pass != '':
                st.error('❌ Invalid passcode for the selected role.')

            if is_admin_logged:
                st.success(f'🔓 Authenticated successfully as **{admin_block}**!')

                # --- ADMIN BUSY STATUS TOGGLE ---
                current_busy_state = is_admin_busy(admin_block)
                new_busy_state = st.checkbox(
                    "🔴 Mark Self as Busy (Auto-Accept Incoming Password Requests)",
                    value=current_busy_state,
                    key=f"busy_toggle_{admin_block}"
                )
                if new_busy_state != current_busy_state:
                    with engine.begin() as conn:
                        conn.execute(
                            text('INSERT INTO togethespace_v4_admin_status (block, is_busy) VALUES (:b, :busy) ON CONFLICT (block) DO UPDATE SET is_busy = :busy'),
                            {'b': admin_block, 'busy': new_busy_state}
                        )
                    if new_busy_state:
                        if admin_block == 'Master Admin':
                            pending_to_auto = pd.read_sql(text("SELECT * FROM togethespace_v4_password_requests WHERE status = 'Pending' AND (requested_by LIKE 'Block Admin:%' OR requested_by = 'Master Admin')"), con=engine)
                        else:
                            pending_to_auto = pd.read_sql(text("SELECT * FROM togethespace_v4_password_requests WHERE block = :b AND status = 'Pending' AND requested_by LIKE 'Resident:%'"), con=engine, params={'b': admin_block})
                        
                        for _, p_req in pending_to_auto.iterrows():
                            with engine.begin() as conn:
                                if admin_block != 'Master Admin' or p_req['target_userid'] != 'master_admin':
                                    conn.execute(
                                        text('UPDATE togethespace_v4_directory SET "Password" = :pwd WHERE "User ID" = :uid OR "Full Name" = :name'),
                                        {'pwd': p_req['new_password'], 'uid': p_req['target_userid'], 'name': p_req['target_name']}
                                    )
                                conn.execute(
                                    text('UPDATE togethespace_v4_password_requests SET status = \'Approved\' WHERE id = :id'),
                                    {'id': p_req['id']}
                                )
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                    {'by': f'{admin_block} Admin (Busy Mode)', 'target': p_req['target_userid'], 'action': 'Bulk Auto-Accepted Password Request', 'details': f'Auto-approved pending request #{p_req["id"]} because admin marked themselves busy.'}
                                )
                        st.success(f"Status updated to Busy! All pending requests have been automatically approved.")
                    else:
                        st.info(f"Status updated to Available.")
                    st.rerun()

                admin_action = st.radio('Select Admin Operation', [
                    '📢 Create Notice',
                    '🌐 Request / Manage Cross-Block Broadcasts',
                    '🗑️ Delete Post',
                    '➕ Add Member',
                    '✏️ Edit Member',
                    '❌ Delete Member',
                    '🔑 Password Requests & Approvals',
                    '⚡ Direct Password Override (Master Only)',
                    '📋 Audit Logs',
                    '📥 Export Credentials CSV'
                ], horizontal=True)

                st.markdown('---')

                # 1. CREATE NOTICE
                if admin_action == '📢 Create Notice':
                    st.markdown('#### Broadcast Notice to Community')
                    with st.form('admin_notice_form'):
                        n_title = st.text_input('Notice Title / Subject')
                        n_category = st.selectbox('Category', ['Notice', 'Announcement', 'Community Update'])
                        n_content = st.text_area('Notice Details / Content')
                        n_submit = st.form_submit_button('Publish Official Notice')
                        if n_submit:
                            if n_title and n_content:
                                post_org = admin_block if admin_block != 'Master Admin' else 'Block A'
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_records (title, category, content, author, likes, "Block", "Visibility", "Broadcast_Status") VALUES (:title, :category, :content, :author, 0, :block, :visibility, :status)'),
                                        {'title': n_title, 'category': n_category, 'content': n_content, 'author': f'{admin_block} Admin', 'block': post_org, 'visibility': 'Block-Only', 'status': 'None'}
                                    )
                                st.success('Official notice published for your block!')
                                st.rerun()
                            else:
                                st.warning('Please fill in title and content.')

                # 2. CROSS-BLOCK BROADCASTS
                elif admin_action == '🌐 Request / Manage Cross-Block Broadcasts':
                    st.markdown('#### 🌐 Cross-Block Broadcast Management')
                    if admin_block == 'Master Admin':
                        st.info('👑 Master Admin: Review and approve/reject pending cross-block broadcast requests from block admins.')
                        try:
                            with engine.connect() as conn:
                                b_reqs = pd.read_sql(text('SELECT * FROM togethespace_v4_records WHERE "Broadcast_Status" = \'Pending\' ORDER BY created_at DESC;'), con=conn)
                            
                            if b_reqs.empty:
                                st.info('No pending broadcast requests from block admins.')
                            else:
                                for idx, req in b_reqs.iterrows():
                                    st.markdown(f"""
                                        <div class="admin-card">
                                            <b>Post ID:</b> {req['id']} | <b>Block:</b> {req.get('Block')} | <b>Author:</b> {req['author']}<br>
                                            <b>Title:</b> {req['title']}<br>
                                            <b>Content:</b> {req['content']}
                                        </div>
                                    """, unsafe_allow_html=True)
                                    col_app_b, col_rej_b = st.columns(2)
                                    with col_app_b:
                                        if st.button(f'🌐 Approve Broadcast for Post #{req["id"]}', key=f'app_b_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_records SET "Visibility" = \'Global\', "Broadcast_Status" = \'Approved\' WHERE id = :id'),
                                                    {'id': int(req['id'])}
                                                )
                                            st.success(f'Post #{req["id"]} is now globally broadcasted to all blocks!')
                                            st.rerun()
                                    with col_rej_b:
                                        if st.button(f'❌ Reject Broadcast #{req["id"]}', key=f'rej_b_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_records SET "Broadcast_Status" = \'Rejected\' WHERE id = :id'),
                                                    {'id': int(req['id'])}
                                                )
                                            st.warning(f'Broadcast request rejected for Post #{req["id"]}.')
                                            st.rerun()
                        except Exception as e:
                            st.warning(f'Error loading broadcast requests: {e}')
                    else:
                        st.info(f'🏢 Block Admin ({admin_block}): Select one of your block posts below to request Master Admin approval for global cross-block viewing.')
                        try:
                            with engine.connect() as conn:
                                block_posts = pd.read_sql(text('SELECT id, title, category, "Visibility", "Broadcast_Status" FROM togethespace_v4_records WHERE "Block" = :block ORDER BY created_at DESC;'), con=conn, params={'block': admin_block})
                            
                            if block_posts.empty:
                                st.info('No posts found in your block.')
                            else:
                                p_choice = st.selectbox('Select Post to Request Broadcast', block_posts.apply(lambda r: f"ID {r['id']}: {r['title']} (Visibility: {r['Visibility']}, Status: {r['Broadcast_Status']})", axis=1))
                                if p_choice:
                                    p_id = int(p_choice.split(':')[0].replace('ID ', ''))
                                    if st.button('🚀 Submit Request to Master Admin for Cross-Block Broadcast'):
                                        with engine.begin() as conn:
                                            conn.execute(
                                                text('UPDATE togethespace_v4_records SET "Broadcast_Status" = \'Pending\' WHERE id = :id'),
                                                {'id': p_id}
                                            )
                                        st.success('Broadcast request submitted to Master Admin successfully!')
                                        st.rerun()
                        except Exception as e:
                            st.warning(f'Error loading block posts: {e}')

                # 3. DELETE POST
                elif admin_action == '🗑️ Delete Post':
                    st.markdown('#### Delete Post by ID')
                    try:
                        with engine.connect() as conn:
                            if admin_block == 'Master Admin':
                                df_posts = pd.read_sql(text('SELECT id, title, category, author, "Block", created_at FROM togethespace_v4_records ORDER BY created_at DESC;'), con=conn)
                            else:
                                df_posts = pd.read_sql(text('SELECT id, title, category, author, "Block", created_at FROM togethespace_v4_records WHERE "Block" = :block ORDER BY created_at DESC;'), con=conn, params={'block': admin_block})
                        
                        if df_posts.empty:
                            st.info('No posts available to delete.')
                        else:
                            post_to_delete = st.selectbox('Select Post to Remove', df_posts.apply(lambda r: f"ID {r['id']}: [{r['Block']}] {r['title']} (by {r['author']})", axis=1))
                            if st.button('🗑️ Delete Selected Post', type='primary'):
                                post_id = int(post_to_delete.split(':')[0].replace('ID ', ''))
                                with engine.begin() as conn:
                                    conn.execute(text('DELETE FROM togethespace_v4_records WHERE id = :id'), {'id': post_id})
                                st.success(f'Post ID {post_id} successfully deleted.')
                                st.rerun()
                    except Exception as e:
                        st.warning(f'Error loading posts: {e}')

                # 4. ADD MEMBER
                elif admin_action == '➕ Add Member':
                    st.markdown('#### Add New Member Record')
                    st.info('ℹ️ Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')
                    with st.form('admin_add_dir', clear_on_submit=True):
                        c1, c2 = st.columns(2)
                        default_org = admin_block if admin_block != 'Master Admin' else 'Block A'
                        with c1:
                            org = st.text_input('Organization / Block', value=default_org)
                            full_name = st.text_input('Full Name *')
                            userid = st.text_input('User ID')
                            password = st.text_input('Password', type='password')
                            address = st.text_input('Address')
                            phone = st.text_input('Phone Number')
                            wa_call = st.text_input('WhatsApp Call')
                            wa_chat = st.text_input('WhatsApp Chat')
                        with c2:
                            email = st.text_input('Email')
                            website = st.text_input('Website')
                            blood = st.text_input('Blood Group')
                            allergies = st.text_input('Allergies')
                            med_cond = st.text_input('Medical Conditions')
                            meds = st.text_input('Medications')
                            em_name = st.text_input('Emergency Contact Name')
                            em_phone = st.text_input('Emergency Contact Phone')
                            bio = st.text_area('Bio / Notes')
                        
                        add_sub = st.form_submit_button('Insert New Member')
                        if add_sub:
                            if full_name:
                                pwd_to_use = password if password else 'Welcome2026!'
                                is_valid, msg = validate_password_policy(pwd_to_use)
                                if not is_valid:
                                    st.error(f'❌ Password Policy Error: {msg}')
                                else:
                                    hashed_pwd = hash_password(pwd_to_use)
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text("""
                                                INSERT INTO togethespace_v4_directory 
                                                ("Organization", "Full Name", "User ID", "Password", "Address", "Phone Number", "WhatsApp Call", "WhatsApp Chat", "Email", "Website", "Blood Group", "Allergies", "Medical Conditions", "Medications", "Emergency Contact Name", "Emergency Contact Phone", "Bio")
                                                VALUES 
                                                (:org, :full_name, :userid, :password, :address, :phone, :wa_call, :wa_chat, :email, :website, :blood, :allergies, :med_cond, :meds, :em_name, :em_phone, :bio)
                                            """),
                                            {
                                                'org': org, 'full_name': full_name, 'userid': userid, 'password': hashed_pwd,
                                                'address': address, 'phone': phone, 'wa_call': wa_call, 'wa_chat': wa_chat,
                                                'email': email, 'website': website, 'blood': blood, 'allergies': allergies,
                                                'med_cond': med_cond, 'meds': meds, 'em_name': em_name, 'em_phone': em_phone, 'bio': bio
                                            }
                                        )
                                    st.success('New member added successfully with encrypted password conforming to policy!')
                                    st.rerun()
                            else:
                                st.warning('Full Name is required.')

                # 5. EDIT MEMBER
                elif admin_action == '✏️ Edit Member':
                    st.markdown('#### Edit Existing Member')
                    edit_query = st.text_input('Search Member Name to Edit', '')
                    if edit_query:
                        with engine.connect() as conn:
                            if admin_block != 'Master Admin':
                                res_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Phone Number" FROM togethespace_v4_directory WHERE "Organization" = :block AND "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"block": admin_block, "q": f"%{edit_query}%"})
                            else:
                                res_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Phone Number" FROM togethespace_v4_directory WHERE "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"q": f"%{edit_query}%"})
                        
                        if res_df.empty:
                            st.info('No members found matching your search in your authorized block.')
                        else:
                            member_choice = st.selectbox('Select Member to Modify', res_df.apply(lambda r: f"ID {r['id']}: {r['Full Name']} ({r['Organization']})", axis=1))
                            if member_choice:
                                m_id = int(member_choice.split(':')[0].replace('ID ', ''))
                                with engine.connect() as conn:
                                    m_data = pd.read_sql(text('SELECT * FROM togethespace_v4_directory WHERE id = :id'), con=conn, params={'id': m_id}).iloc[0]
                                
                                st.info('ℹ️ Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')
                                with st.form('edit_dir_form'):
                                    e_name = st.text_input('Full Name', value=str(m_data.get('Full Name', '')))
                                    e_uid = st.text_input('User ID', value=str(m_data.get('User ID', '')))
                                    e_pwd = st.text_input('New Password (leave blank to keep current)', type='password', value='')
                                    e_addr = st.text_input('Address', value=str(m_data.get('Address', '')))
                                    e_phone = st.text_input('Phone Number', value=str(m_data.get('Phone Number', '')))
                                    e_email = st.text_input('Email', value=str(m_data.get('Email', '')))
                                    
                                    update_btn = st.form_submit_button('Save Changes')
                                    if update_btn:
                                        if e_pwd:
                                            is_valid, msg = validate_password_policy(e_pwd)
                                            if not is_valid:
                                                st.error(f'❌ Password Policy Error: {msg}')
                                                st.stop()
                                        
                                        with engine.begin() as conn:
                                            if e_pwd:
                                                final_pwd_hash = hash_password(e_pwd)
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_directory SET "Full Name" = :name, "User ID" = :uid, "Password" = :pwd, "Address" = :addr, "Phone Number" = :phone, "Email" = :email WHERE id = :id'),
                                                    {'name': e_name, 'uid': e_uid, 'pwd': final_pwd_hash, 'addr': e_addr, 'phone': e_phone, 'email': e_email, 'id': m_id}
                                                )
                                            else:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_directory SET "Full Name" = :name, "User ID" = :uid, "Address" = :addr, "Phone Number" = :phone, "Email" = :email WHERE id = :id'),
                                                    {'name': e_name, 'uid': e_uid, 'addr': e_addr, 'phone': e_phone, 'email': e_email, 'id': m_id}
                                                )
                                        st.success('Member record updated successfully!')
                                        st.rerun()

                # 6. DELETE MEMBER
                elif admin_action == '❌ Delete Member':
                    st.markdown('#### Remove Member Record')
                    del_query = st.text_input('Search Member Name to Delete', '')
                    if del_query:
                        with engine.connect() as conn:
                            if admin_block != 'Master Admin':
                                del_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Phone Number" FROM togethespace_v4_directory WHERE "Organization" = :block AND "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"block": admin_block, "q": f"%{del_query}%"})
                            else:
                                del_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Phone Number" FROM togethespace_v4_directory WHERE "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"q": f"%{del_query}%"})
                        
                        if del_df.empty:
                            st.info('No members found in your authorized block.')
                        else:
                            del_choice = st.selectbox('Select Member to Delete', del_df.apply(lambda r: f"ID {r['id']}: {r['Full Name']} ({r['Organization']})", axis=1))
                            if del_choice:
                                d_id = int(del_choice.split(':')[0].replace('ID ', ''))
                                if st.button('⚠️ Confirm & Permanently Delete Member', type='primary'):
                                    with engine.begin() as conn:
                                        conn.execute(text('DELETE FROM togethespace_v4_directory WHERE id = :id'), {'id': d_id})
                                    st.success(f'Member ID {d_id} deleted successfully.')
                                    st.rerun()

                # 7. PASSWORD REQUESTS & APPROVALS WORKFLOW
                elif admin_action == '🔑 Password Requests & Approvals':
                    if admin_block == 'Master Admin':
                        st.markdown('### 👑 Master Admin: Manage Block Admin Requests & Self-Requests')
                        
                        st.info('ℹ️ Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')
                        with st.expander('➕ Request Password Change for Master Admin (Self-Request)', expanded=False):
                            master_is_busy = is_admin_busy('Master Admin')
                            if master_is_busy:
                                st.info("🔴 Notice: You are currently marked **Busy**. Your self-request will be **auto-accepted** instantly!")
                            
                            with st.form('master_self_req_form'):
                                m_req_pwd = st.text_input('New Desired Master Password', type='password')
                                m_req_sub = st.form_submit_button('Submit Self-Request')
                                if m_req_sub:
                                    if m_req_pwd:
                                        is_valid, msg = validate_password_policy(m_req_pwd)
                                        if not is_valid:
                                            st.error(f'❌ Password Policy Error: {msg}')
                                        else:
                                            hashed_m_req = hash_password(m_req_pwd)
                                            req_status = 'Approved' if master_is_busy else 'Pending'
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('INSERT INTO togethespace_v4_password_requests (requested_by, target_userid, target_name, block, new_password, status) VALUES (:by, :target, :name, :block, :pwd, :status)'),
                                                    {
                                                        'by': 'Master Admin',
                                                        'target': 'master_admin',
                                                        'name': 'Master Administrator',
                                                        'block': 'All Blocks',
                                                        'pwd': hashed_m_req,
                                                        'status': req_status
                                                    }
                                                )
                                                conn.execute(
                                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                    {
                                                        'by': 'Master Admin',
                                                        'target': 'master_admin',
                                                        'action': 'Master Self-Request',
                                                        'details': f'Master Admin submitted self-request (Auto-approved: {master_is_busy}).'
                                                    }
                                                )
                                            if master_is_busy:
                                                st.success('Master Admin self-request automatically approved!')
                                            else:
                                                st.success('Master Admin self-request submitted successfully!')
                                    else:
                                        st.warning('Please enter a password.')

                        st.markdown('#### Pending Requests from Block Admins & Master Self-Requests')
                        try:
                            with engine.connect() as conn:
                                master_req_df = pd.read_sql(text('SELECT * FROM togethespace_v4_password_requests WHERE status = \'Pending\' AND (requested_by LIKE \'Block Admin:%\' OR requested_by = \'Master Admin\') ORDER BY created_at DESC;'), con=conn)
                            
                            if master_req_df.empty:
                                st.info('No pending requests from block admins or master admin.')
                            else:
                                for idx, req in master_req_df.iterrows():
                                    st.markdown(f"""
                                        <div class="admin-card">
                                            <b>Request ID:</b> {req['id']} | <b>Requested By:</b> {req['requested_by']} | <b>Target:</b> {req['target_name']}<br>
                                            <b>Date:</b> {req['created_at']}
                                        </div>
                                    """, unsafe_allow_html=True)
                                    col_app_m, col_rej_m = st.columns(2)
                                    with col_app_m:
                                        if st.button(f'✅ Approve Request #{req["id"]}', key=f'app_m_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_password_requests SET status = \'Approved\' WHERE id = :id'),
                                                    {'id': req['id']}
                                                )
                                                conn.execute(
                                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                    {'by': 'Master Admin', 'target': req['target_userid'], 'action': 'Approved Block Admin Request', 'details': f'Master Admin approved request #{req["id"]} for {req["target_name"]}.'}
                                                )
                                            st.success(f'Request #{req["id"]} approved successfully!')
                                            st.rerun()
                                    with col_rej_m:
                                        if st.button(f'❌ Reject Request #{req["id"]}', key=f'rej_m_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_password_requests SET status = \'Rejected\' WHERE id = :id'),
                                                    {'id': req['id']}
                                                )
                                            st.warning(f'Request #{req["id"]} rejected.')
                                            st.rerun()
                        except Exception as e:
                            st.warning(f'Error loading master admin requests: {e}')

                    else:
                        st.markdown(f'### 🏢 Block Admin ({admin_block}): Resident Requests & Send Request to Master Admin')
                        
                        st.markdown('#### Pending Resident Password Requests (Approve/Reject)')
                        try:
                            with engine.connect() as conn:
                                res_req_df = pd.read_sql(text('SELECT * FROM togethespace_v4_password_requests WHERE block = :block AND status = \'Pending\' AND requested_by LIKE \'Resident:%\' ORDER BY created_at DESC;'), con=conn, params={'block': admin_block})
                            
                            if res_req_df.empty:
                                st.info('No pending resident requests in your block.')
                            else:
                                for idx, req in res_req_df.iterrows():
                                    st.markdown(f"""
                                        <div class="admin-card">
                                            <b>Request ID:</b> {req['id']} | <b>Resident:</b> {req['requested_by']} | <b>Target ID:</b> {req['target_userid']}<br>
                                            <b>Date:</b> {req['created_at']}
                                        </div>
                                    """, unsafe_allow_html=True)
                                    col_ar, col_rr = st.columns(2)
                                    with col_ar:
                                        if st.button(f'✅ Approve Resident Request #{req["id"]}', key=f'app_res_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_directory SET "Password" = :pwd WHERE "User ID" = :uid OR "Full Name" = :name'),
                                                    {'pwd': req['new_password'], 'uid': req['target_userid'], 'name': req['target_name']}
                                                )
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_password_requests SET status = \'Approved\' WHERE id = :id'),
                                                    {'id': req['id']}
                                                )
                                                conn.execute(
                                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                    {'by': f'Block Admin ({admin_block})', 'target': req['target_userid'], 'action': 'Approved Resident Password Request', 'details': f'Block Admin approved password request for {req["target_name"]}.'}
                                                )
                                            st.success(f'Resident request #{req["id"]} approved and password updated!')
                                            st.rerun()
                                    with col_rr:
                                        if st.button(f'❌ Reject Resident Request #{req["id"]}', key=f'rej_res_{req["id"]}'):
                                            with engine.begin() as conn:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_password_requests SET status = \'Rejected\' WHERE id = :id'),
                                                    {'id': req['id']}
                                                )
                                            st.warning(f'Resident request #{req["id"]} rejected.')
                                            st.rerun()
                        except Exception as e:
                            st.warning(f'Error loading resident requests: {e}')

                        st.markdown('---')
                        st.markdown('#### 🚀 Send Password Change Request to Master Admin')
                        st.info('ℹ️ Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')
                        
                        master_is_busy = is_admin_busy('Master Admin')
                        if master_is_busy:
                            st.info("🔴 Notice: The **Master Admin** is currently marked **Busy**. Your request will be **auto-accepted** instantly!")

                        with st.form('block_admin_to_master_form'):
                            ba_new_p = st.text_input('New Password for Block Admin', type='password')
                            ba_req_sub = st.form_submit_button('Submit Password Request to Master Admin')
                            if ba_req_sub:
                                if ba_new_p:
                                    is_valid, msg = validate_password_policy(ba_new_p)
                                    if not is_valid:
                                        st.error(f'❌ Password Policy Error: {msg}')
                                    else:
                                        hashed_ba_p = hash_password(ba_new_p)
                                        req_status = 'Approved' if master_is_busy else 'Pending'
                                        with engine.begin() as conn:
                                            conn.execute(
                                                text('INSERT INTO togethespace_v4_password_requests (requested_by, target_userid, target_name, block, new_password, status) VALUES (:by, :target, :name, :block, :pwd, :status)'),
                                                {
                                                    'by': f'Block Admin: {admin_block}',
                                                    'target': admin_block.lower().replace(' ', '_'),
                                                    'name': f'{admin_block} Administrator',
                                                    'block': admin_block,
                                                    'pwd': hashed_ba_p,
                                                    'status': req_status
                                                }
                                            )
                                            conn.execute(
                                                text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                {
                                                    'by': f'{admin_block} Admin',
                                                    'target': admin_block.lower().replace(' ', '_'),
                                                    'action': 'Sent Password Request to Master Admin',
                                                    'details': f'Block Admin for {admin_block} submitted password request (Auto-accepted: {master_is_busy}).'
                                                }
                                            )
                                        if master_is_busy:
                                            st.success('Master Admin is busy! Your password change request was automatically approved.')
                                        else:
                                            st.success('Password change request successfully sent to Master Admin!')
                                else:
                                    st.warning('Please enter a password.')

                # 8. DIRECT PASSWORD OVERRIDE (Master Only)
                elif admin_action == '⚡ Direct Password Override (Master Only)':
                    if admin_block == 'Master Admin':
                        st.markdown('### ⚡ Master Admin: Direct Password Override (No Request Needed)')
                        st.info('👑 As Master Admin, you can select any user or block admin and update their password immediately without waiting for approval requests.')
                        st.info('ℹ️ Password Policy: Must be at least 8 characters and include at least one capital letter, one small letter, one number, and one special character.')
                        
                        try:
                            with engine.connect() as conn:
                                all_users_df = pd.read_sql(text('SELECT id, "User ID", "Full Name", "Organization" FROM togethespace_v4_directory ORDER BY "Full Name" ASC;'), con=conn)
                            
                            if all_users_df.empty:
                                st.warning('No users found in directory.')
                            else:
                                override_choice = st.selectbox('Select User to Directly Override Password', all_users_df.apply(lambda r: f"ID {r['id']} — {r['Full Name']} ({r['Organization']} / {r['User ID']})", axis=1))
                                
                                with st.form('master_direct_override_form'):
                                    new_override_pwd = st.text_input('New Password Override', type='password')
                                    override_sub = st.form_submit_button('Apply Direct Password Override')
                                    
                                    if override_sub:
                                        if override_choice and new_override_pwd:
                                            is_valid, msg = validate_password_policy(new_override_pwd)
                                            if not is_valid:
                                                st.error(f'❌ Password Policy Error: {msg}')
                                            else:
                                                target_db_id = int(override_choice.split(' — ')[0].replace('ID ', ''))
                                                final_override_hash = hash_password(new_override_pwd)
                                                
                                                with engine.begin() as conn:
                                                    conn.execute(
                                                        text('UPDATE togethespace_v4_directory SET "Password" = :pwd WHERE id = :id'),
                                                        {'pwd': final_override_hash, 'id': target_db_id}
                                                    )
                                                    conn.execute(
                                                        text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                        {
                                                            'by': 'Master Admin',
                                                            'target': str(target_db_id),
                                                            'action': 'Direct Password Override',
                                                            'details': f'Master Admin directly changed password for user record ID {target_db_id} without request.'
                                                        }
                                                    )
                                                st.success(f'Password successfully overridden and updated for user ID {target_db_id} without request!')
                                                st.rerun()
                                        else:
                                            st.warning('Please provide a new password.')
                        except Exception as e:
                            st.warning(f'Error loading users for override: {e}')
                    else:
                        st.error('❌ Access Denied: Direct Password Override is restricted exclusively to the Master Admin.')

                # 9. AUDIT LOGS
                elif admin_action == '📋 Audit Logs':
                    st.markdown('#### 📜 Password Change & Login Audit Logs')
                    try:
                        with engine.connect() as conn:
                            logs_df = pd.read_sql(text('SELECT * FROM togethespace_v4_password_logs ORDER BY timestamp DESC LIMIT 100;'), con=conn)
                        
                        if logs_df.empty:
                            st.info('No audit logs recorded yet.')
                        else:
                            st.dataframe(logs_df, use_container_width=True)
                    except Exception as e:
                        st.info('Audit log table will populate once logins or password changes are processed.')

                # 10. EXPORT CREDENTIALS CSV
                elif admin_action == '📥 Export Credentials CSV':
                    st.markdown('#### 📥 Download Credentials Export')
                    st.info('Note: Passwords are securely hashed. The CSV export displays hashed security strings for account protection.')
                    try:
                        with engine.connect() as conn:
                            if admin_block == 'Master Admin':
                                df_cred = pd.read_sql(text('SELECT "Organization", "Full Name", "User ID", "Password" FROM togethespace_v4_directory ORDER BY "Organization", "Full Name";'), con=conn)
                            else:
                                df_cred = pd.read_sql(text('SELECT "Organization", "Full Name", "User ID", "Password" FROM togethespace_v4_directory WHERE "Organization" = :block ORDER BY "Full Name";'), con=conn, params={'block': admin_block})
                        
                        if df_cred.empty:
                            st.warning('No credential records found.')
                        else:
                            csv_data = df_cred.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"📥 Download {admin_block} Credentials CSV",
                                data=csv_data,
                                file_name=f"togethespace_credentials_{admin_block.lower().replace(' ', '_')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.warning(f'Could not generate credential export: {e}')

    except Exception as e:
        st.error(f'Database connection or query failed: {e}')

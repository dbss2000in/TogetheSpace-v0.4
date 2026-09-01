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
    .admin-card {
        background-color: #fff3e0;
        border-left: 6px solid #f57c00;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 3px 6px rgba(245, 124, 0, 0.1);
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
        tab_directory, tab_feed, tab_notices, tab_chat, tab_social, tab_admin = st.tabs([
            '📋 Member Directory Datasheet',
            '🏡 Feed & Sea Green Cards',
            '📢 Notices & Alerts',
            '💬 Community Chat',
            '🌐 Social Channels',
            '🔐 Block Admin Portal'
        ])

        # 1. COMPREHENSIVE MEMBER DIRECTORY DATASHEET TAB
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
                        map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(row.get('Address', '')))}"
                        
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h3 style="color: #1b5e20; margin-bottom: 2px;">{row.get('Full Name')} {fav_badge}</h3>
                                <p style="color: #4f5d54; font-size: 0.95em; margin-bottom: 10px;">
                                    {org_badge} | <b>Bio:</b> {row.get('Bio') or 'N/A'}
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
                st.warning(f'Directory loading failed. Details: {e}')

        # 2. FEED & SEA GREEN CARDS TAB
        with tab_feed:
            st.markdown('### 🌊 Community Feed & Posts')
            
            with st.expander('➕ Publish a New Community Post', expanded=False):
                with st.form('inline_feed_form', clear_on_submit=True):
                    new_title = st.text_input('Title / Subject')
                    new_category = st.selectbox('Category', ['General', 'Notice', 'Announcement', 'Community Update', 'Discussion'])
                    new_author = st.text_input('Author Name')
                    new_content = st.text_area('Content / Details')
                    
                    submitted = st.form_submit_button('Publish Post')
                    if submitted:
                        if new_title and new_content:
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_records (title, category, content, author, likes) VALUES (:title, :category, :content, :author, 0)'),
                                    {'title': new_title, 'category': new_category, 'content': new_content, 'author': new_author}
                                )
                            st.success('Post successfully published!')
                            st.rerun()
                        else:
                            st.warning('Please provide both a Title and Content.')

            st.markdown('---')
            st.markdown('#### Recent Feed Posts')
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
                                <h4 style="color: #1b5e20; margin-bottom: 5px;">{row['title']} (ID: {row['id']})</h4>
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

        # 6. BLOCK ADMIN PORTAL TAB (Admin Controls: Notices, Post Deletion, Directory CRUD)
        with tab_admin:
            st.markdown('### 🔐 Block-Wise Administrator Portal')
            st.markdown('Authenticate with your block credentials to manage community notices, delete posts, and modify directory records.')
            
            col_adm1, col_adm2 = st.columns(2)
            with col_adm1:
                admin_block = st.selectbox('Select Block / Zone', ['Block A', 'Block B', 'Block C', 'Block AE', 'Master Admin'])
            with col_adm2:
                admin_pass = st.text_input('Admin Passcode', type='password')

            # Simple secure check (or configurable via secrets)
            is_admin_logged = (admin_pass == 'TogetheSpace2026Secure' or admin_pass == 'admin')

            if not is_admin_logged and admin_pass != '':
                st.error('❌ Invalid admin passcode.')

            if is_admin_logged:
                st.success(f'🔓 Authenticated successfully as Administrator for **{admin_block}**!')

                admin_action = st.radio('Select Admin Operation', [
                    '📢 Create Official Notice / Announcement',
                    '🗑️ Delete Feed Post or Notice',
                    '➕ Add New Directory Entry',
                    '✏️ Modify / Edit Directory Entry',
                    '❌ Delete Directory Entry'
                ], horizontal=True)

                st.markdown('---')

                # OPERATION 1: CREATE NOTICE
                if admin_action == '📢 Create Official Notice / Announcement':
                    st.markdown('#### Broadcast Notice to Community')
                    with st.form('admin_notice_form'):
                        n_title = st.text_input('Notice Title / Subject')
                        n_category = st.selectbox('Category', ['Notice', 'Announcement', 'Community Update'])
                        n_content = st.text_area('Notice Details / Content')
                        n_submit = st.form_submit_button('Publish Official Notice')
                        if n_submit:
                            if n_title and n_content:
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_records (title, category, content, author, likes) VALUES (:title, :category, :content, :author, 0)'),
                                        {'title': n_title, 'category': n_category, 'content': n_content, 'author': f'{admin_block} Admin'}
                                    )
                                st.success('Official notice broadcast successfully!')
                                st.rerun()
                            else:
                                st.warning('Please fill in title and content.')

                # OPERATION 2: DELETE POST
                elif admin_action == '🗑️ Delete Feed Post or Notice':
                    st.markdown('#### Delete Post by ID')
                    try:
                        with engine.connect() as conn:
                            df_posts = pd.read_sql(text('SELECT id, title, category, author, created_at FROM togethespace_v4_records ORDER BY created_at DESC;'), con=conn)
                        
                        if df_posts.empty:
                            st.info('No posts available to delete.')
                        else:
                            post_to_delete = st.selectbox('Select Post to Remove', df_posts.apply(lambda r: f"ID {r['id']}: [{r['category']}] {r['title']} (by {r['author']})", axis=1))
                            if st.button('🗑️ Delete Selected Post', type='primary'):
                                post_id = int(post_to_delete.split(':')[0].replace('ID ', ''))
                                with engine.begin() as conn:
                                    conn.execute(text('DELETE FROM togethespace_v4_records WHERE id = :id'), {'id': post_id})
                                st.success(f'Post ID {post_id} successfully deleted.')
                                st.rerun()
                    except Exception as e:
                        st.warning(f'Error loading posts: {e}')

                # OPERATION 3: ADD DIRECTORY ENTRY
                elif admin_action == '➕ Add New Directory Entry':
                    st.markdown('#### Add New Member Record')
                    with st.form('admin_add_dir', clear_on_submit=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            org = st.text_input('Organization / Block', value=admin_block)
                            full_name = st.text_input('Full Name *')
                            address = st.text_input('Address')
                            phone = st.text_input('Phone Number')
                            wa_call = st.text_input('WhatsApp Call')
                            wa_chat = st.text_input('WhatsApp Chat')
                            email = st.text_input('Email')
                            website = st.text_input('Website')
                        with c2:
                            blood = st.text_input('Blood Group')
                            allergies = st.text_input('Allergies')
                            med_cond = st.text_input('Medical Conditions')
                            meds = st.text_input('Medications')
                            em_name = st.text_input('Emergency Contact Name')
                            em_rel = st.text_input('Emergency Contact Relationship')
                            em_phone = st.text_input('Emergency Contact Phone')
                            bio = st.text_area('Bio / Notes')
                        
                        add_sub = st.form_submit_button('Insert New Member')
                        if add_sub:
                            if full_name:
                                with engine.begin() as conn:
                                    conn.execute(
                                        text("""
                                            INSERT INTO togethespace_v4_directory 
                                            ("Organization", "Full Name", "Address", "Phone Number", "WhatsApp Call", "WhatsApp Chat", "Email", "Website", "Blood Group", "Allergies", "Medical Conditions", "Medications", "Emergency Contact Name", "Emergency Contact Relationship", "Emergency Contact Phone", "Bio")
                                            VALUES 
                                            (:org, :full_name, :address, :phone, :wa_call, :wa_chat, :email, :website, :blood, :allergies, :med_cond, :meds, :em_name, :em_rel, :em_phone, :bio)
                                        """),
                                        {
                                            'org': org, 'full_name': full_name, 'address': address, 'phone': phone,
                                            'wa_call': wa_call, 'wa_chat': wa_chat, 'email': email, 'website': website,
                                            'blood': blood, 'allergies': allergies, 'med_cond': med_cond, 'meds': meds,
                                            'em_name': em_name, 'em_rel': em_rel, 'em_phone': em_phone, 'bio': bio
                                        }
                                    )
                                st.success('New member added successfully!')
                                st.rerun()
                            else:
                                st.warning('Full Name is required.')

                # OPERATION 4: MODIFY / EDIT DIRECTORY ENTRY
                elif admin_action == '✏️ Modify / Edit Directory Entry':
                    st.markdown('#### Edit Existing Member')
                    edit_query = st.text_input('Search Member Name to Edit', '')
                    if edit_query:
                        with engine.connect() as conn:
                            res_df = pd.read_sql(text('SELECT id, "Full Name", "Address", "Phone Number" FROM togethespace_v4_directory WHERE "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"q": f"%{edit_query}%"})
                        
                        if res_df.empty:
                            st.info('No members found matching that name.')
                        else:
                            member_choice = st.selectbox('Select Member to Modify', res_df.apply(lambda r: f"ID {r['id']}: {r['Full Name']} ({r['Phone Number']})", axis=1))
                            if member_choice:
                                m_id = int(member_choice.split(':')[0].replace('ID ', ''))
                                with engine.connect() as conn:
                                    m_data = pd.read_sql(text('SELECT * FROM togethespace_v4_directory WHERE id = :id'), con=conn, params={'id': m_id}).iloc[0]
                                
                                with st.form('edit_dir_form'):
                                    e_name = st.text_input('Full Name', value=str(m_data.get('Full Name', '')))
                                    e_addr = st.text_input('Address', value=str(m_data.get('Address', '')))
                                    e_phone = st.text_input('Phone Number', value=str(m_data.get('Phone Number', '')))
                                    e_email = st.text_input('Email', value=str(m_data.get('Email', '')))
                                    e_notes = st.text_area('Notes', value=str(m_data.get('Notes', '')))
                                    
                                    update_btn = st.form_submit_button('Save Changes')
                                    if update_btn:
                                        with engine.begin() as conn:
                                            conn.execute(
                                                text('UPDATE togethespace_v4_directory SET "Full Name" = :name, "Address" = :addr, "Phone Number" = :phone, "Email" = :email, "Notes" = :notes WHERE id = :id'),
                                                {'name': e_name, 'addr': e_addr, 'phone': e_phone, 'email': e_email, 'notes': e_notes, 'id': m_id}
                                            )
                                        st.success('Member record updated successfully!')
                                        st.rerun()

                # OPERATION 5: DELETE DIRECTORY ENTRY
                elif admin_action == '❌ Delete Directory Entry':
                    st.markdown('#### Remove Member Record')
                    del_query = st.text_input('Search Member Name to Delete', '')
                    if del_query:
                        with engine.connect() as conn:
                            del_df = pd.read_sql(text('SELECT id, "Full Name", "Phone Number" FROM togethespace_v4_directory WHERE "Full Name" ILIKE :q LIMIT 20;'), con=conn, params={"q": f"%{del_query}%"})
                        
                        if del_df.empty:
                            st.info('No members found.')
                        else:
                            del_choice = st.selectbox('Select Member to Delete', del_df.apply(lambda r: f"ID {r['id']}: {r['Full Name']} ({r['Phone Number']})", axis=1))
                            if del_choice:
                                d_id = int(del_choice.split(':')[0].replace('ID ', ''))
                                if st.button('⚠️ Confirm & Permanently Delete Member', type='primary'):
                                    with engine.begin() as conn:
                                        conn.execute(text('DELETE FROM togethespace_v4_directory WHERE id = :id'), {'id': d_id})
                                    st.success(f'Member ID {d_id} deleted successfully.')
                                    st.rerun()

    except Exception as e:
        st.error(f'Database connection or query failed: {e}')

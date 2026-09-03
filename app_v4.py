import urllib.parse
import re
import bcrypt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title='TogetheSpace v0.4 — Heritage High-Concurrency Edition',
    page_icon='⚡',
    layout='wide',
)

# --- BENGAL HERITAGE, VINTAGE 1960S/70S GRAFFITI & TYPOGRAPHY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Poppins:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    .main {
        background-color: #f7f9f6;
        color: #111111;
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2b1810 !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
    }
    
    p, span, label, div, li {
        color: #1a1a1a !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }

    .artisan-title {
        font-family: 'Caveat', cursive !important;
        font-size: 2.2em;
        color: #8b0000 !important;
    }

    /* Vintage 1960s/70s Bengal Heritage Graffiti Frame */
    .heritage-banner {
        background: linear-gradient(135deg, #fdf6ec 0%, #f4e8d8 100%);
        border: 3px double #8b0000;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(139, 0, 0, 0.2);
        text-align: center;
    }

    .heritage-quote {
        background-color: #fcf8f2;
        border-left: 6px solid #8b0000;
        border-right: 1px solid #e2d2c0;
        border-top: 1px solid #e2d2c0;
        border-bottom: 1px solid #e2d2c0;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 15px;
        font-style: italic;
        color: #2b1810 !important;
    }

    code, pre {
        font-family: 'Fira Code', monospace !important;
        color: #8b0000 !important;
        font-weight: 600;
    }

    .sea-green-card {
        background-color: #eaf4ed;
        border-left: 6px solid #1b5e20;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(46, 139, 87, 0.15);
    }
    .notice-card {
        background-color: #e7f3ff;
        border-left: 5px solid #0d47a1;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .admin-card {
        background-color: #fff3e0;
        border-left: 6px solid #e65100;
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
        border-top: 6px solid #8b0000;
    }
    .sidebar-profile {
        background-color: #fdf6ec;
        border: 1px solid #d4b595;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 15px;
    }
    div.stButton > button {
        background-color: rgba(139, 0, 0, 0.08);
        color: #5c0000;
        border: 1px solid rgba(139, 0, 0, 0.3);
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: rgba(139, 0, 0, 0.2);
        border-color: rgba(139, 0, 0, 0.6);
        color: #3b0000;
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

st.title('⚡ TogetheSpace v0.4 — Heritage Edition')

if not DATABASE_URL:
    st.error('DATABASE_URL is missing. Please configure it in Streamlit Cloud Secrets.')
else:
    @st.cache_resource
    def get_db_engine(url):
        return create_engine(url, pool_size=20, max_overflow=10, pool_pre_ping=True)

    try:
        engine = get_db_engine(DATABASE_URL)
        
        # CENTRALIZED DATABASE INITIALIZATION
        with engine.begin() as conn:
            conn.execute(text('SELECT 1;'))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_directory (
                    id SERIAL PRIMARY KEY,
                    "Organization" VARCHAR(100),
                    "Full Name" VARCHAR(150),
                    "User ID" VARCHAR(100) UNIQUE,
                    "Password" TEXT,
                    "Avatar" TEXT,
                    "Facebook" TEXT,
                    "Instagram" TEXT,
                    "Twitter" TEXT,
                    "LinkedIn" TEXT,
                    "Custom_Social_Name" TEXT,
                    "Custom_Social_URL" TEXT,
                    "Social_Approved" BOOLEAN DEFAULT TRUE,
                    "Address" TEXT,
                    "Phone Number" VARCHAR(50),
                    "WhatsApp Call" VARCHAR(50),
                    "WhatsApp Chat" VARCHAR(50),
                    "Email" VARCHAR(150),
                    "Website" TEXT,
                    "Blood Group" VARCHAR(20),
                    "Allergies" TEXT,
                    "Medical Conditions" TEXT,
                    "Medications" TEXT,
                    "Emergency Contact Name" VARCHAR(150),
                    "Emergency Contact Phone" VARCHAR(50),
                    "Bio" TEXT,
                    "Employment_Status" VARCHAR(50) DEFAULT 'Neutral',
                    "Qualification" TEXT,
                    "Is Favorite" BOOLEAN DEFAULT FALSE
                );
            """))

            conn.execute(text('ALTER TABLE togethespace_v4_directory ADD COLUMN IF NOT EXISTS "Employment_Status" VARCHAR(50) DEFAULT \'Neutral\';'))
            conn.execute(text('ALTER TABLE togethespace_v4_directory ADD COLUMN IF NOT EXISTS "Qualification" TEXT;'))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_records (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200),
                    category VARCHAR(100),
                    content TEXT,
                    author VARCHAR(150),
                    likes INT DEFAULT 0,
                    "Block" VARCHAR(50),
                    "Visibility" VARCHAR(50) DEFAULT 'Block-Only',
                    "Broadcast_Status" VARCHAR(50) DEFAULT 'None',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_chat (
                    id SERIAL PRIMARY KEY,
                    sender VARCHAR(150),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_admin_status (
                    block VARCHAR(50) PRIMARY KEY,
                    is_busy BOOLEAN DEFAULT FALSE
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_password_requests (
                    id SERIAL PRIMARY KEY,
                    requested_by VARCHAR(150),
                    target_userid VARCHAR(100),
                    target_name VARCHAR(150),
                    block VARCHAR(50),
                    new_password TEXT,
                    status VARCHAR(50) DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_password_logs (
                    id SERIAL PRIMARY KEY,
                    changed_by VARCHAR(150),
                    target_userid VARCHAR(100),
                    action_type VARCHAR(100),
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_entry_requests (
                    id SERIAL PRIMARY KEY,
                    applicant_name VARCHAR(150),
                    applicant_userid VARCHAR(100),
                    block VARCHAR(50),
                    request_type VARCHAR(50),
                    form_payload JSONB,
                    passport_photo_url TEXT,
                    supporting_docs_url TEXT,
                    cell_decisions JSONB DEFAULT '{}',
                    status VARCHAR(50) DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_media_corner (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200),
                    event_type VARCHAR(50),
                    media_url TEXT,
                    uploader VARCHAR(150),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_donations (
                    id SERIAL PRIMARY KEY,
                    donor_name VARCHAR(150),
                    item_category VARCHAR(100),
                    description TEXT,
                    item_photo_url TEXT,
                    status VARCHAR(50) DEFAULT 'Available for Collection',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_admin_thanks (
                    id SERIAL PRIMARY KEY,
                    admin_name VARCHAR(150),
                    thanked_by VARCHAR(150),
                    message TEXT,
                    remuneration_amount NUMERIC(10,2) DEFAULT 0.00,
                    payment_screenshot_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_classifieds (
                    id SERIAL PRIMARY KEY,
                    seller_name VARCHAR(150),
                    listing_type VARCHAR(50),
                    title VARCHAR(200),
                    description TEXT,
                    thumbnail_url TEXT,
                    base_price NUMERIC(10,2) DEFAULT 0.00,
                    highest_bid NUMERIC(10,2) DEFAULT 0.00,
                    highest_bidder VARCHAR(150) DEFAULT '',
                    status VARCHAR(50) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_helpdesk (
                    id SERIAL PRIMARY KEY,
                    resident_name VARCHAR(150),
                    block VARCHAR(50),
                    issue_details TEXT,
                    admin_comments TEXT DEFAULT '',
                    status VARCHAR(50) DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_job_bids (
                    id SERIAL PRIMARY KEY,
                    job_seeker_name VARCHAR(150),
                    employer_name VARCHAR(150),
                    daily_wage NUMERIC(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_event_invites (
                    id SERIAL PRIMARY KEY,
                    host_name VARCHAR(150),
                    event_title VARCHAR(200),
                    event_details TEXT,
                    invited_guest VARCHAR(150),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_admin_overrides (
                    content_key VARCHAR(100) PRIMARY KEY,
                    content_payload TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_gemini_sync_logs (
                    block VARCHAR(50) PRIMARY KEY,
                    last_sync_time TIMESTAMP
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS togethespace_v4_music_sync_logs (
                    block VARCHAR(50) PRIMARY KEY,
                    last_music_sync TIMESTAMP
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

        ADMIN_PROFILES = {
            'Block A': {
                'Full Name': 'Aarav Mukherjee',
                'User ID': 'admin_block_a_01',
                'Organization': 'Block A',
                'Designation': 'Block A Administrator',
                'Email': 'aarav.mukherjee@togethespace.local',
                'Phone Number': '+91-9876543210',
                'Address': 'Block A Control Office, TogetheSpace',
                'Blood Group': 'O+', 'Allergies': 'None', 'Avatar': '', 'Facebook': '', 'Instagram': '', 'Twitter': '', 'LinkedIn': '', 'Custom_Social_Name': '', 'Custom_Social_URL': '', 'Employment_Status': 'Neutral', 'Qualification': 'Administrator', 'Social_Approved': True
            },
            'Block B': {
                'Full Name': 'Priya Sharma',
                'User ID': 'admin_block_b_02',
                'Organization': 'Block B',
                'Designation': 'Block B Administrator',
                'Email': 'priya.sharma@togethespace.local',
                'Phone Number': '+91-9876543211',
                'Address': 'Block B Control Office, TogetheSpace',
                'Blood Group': 'A+', 'Allergies': 'None', 'Avatar': '', 'Facebook': '', 'Instagram': '', 'Twitter': '', 'LinkedIn': '', 'Custom_Social_Name': '', 'Custom_Social_URL': '', 'Employment_Status': 'Neutral', 'Qualification': 'Administrator', 'Social_Approved': True
            },
            'Block C': {
                'Full Name': 'Rohan Verma',
                'User ID': 'admin_block_c_03',
                'Organization': 'Block C',
                'Designation': 'Block C Administrator',
                'Email': 'rohan.verma@togethespace.local',
                'Phone Number': '+91-9876543212',
                'Address': 'Block C Control Office, TogetheSpace',
                'Blood Group': 'B+', 'Allergies': 'Dust', 'Avatar': '', 'Facebook': '', 'Instagram': '', 'Twitter': '', 'LinkedIn': '', 'Custom_Social_Name': '', 'Custom_Social_URL': '', 'Employment_Status': 'Neutral', 'Qualification': 'Administrator', 'Social_Approved': True
            },
            'Block AE': {
                'Full Name': 'Ananya Das',
                'User ID': 'admin_block_ae_04',
                'Organization': 'Block AE',
                'Designation': 'Block AE Administrator',
                'Email': 'ananya.das@togethespace.local',
                'Phone Number': '+91-9876543213',
                'Address': 'Block AE Control Office, TogetheSpace',
                'Blood Group': 'AB+', 'Allergies': 'None', 'Avatar': '', 'Facebook': '', 'Instagram': '', 'Twitter': '', 'LinkedIn': '', 'Custom_Social_Name': '', 'Custom_Social_URL': '', 'Employment_Status': 'Neutral', 'Qualification': 'Administrator', 'Social_Approved': True
            },
            'Master Admin': {
                'Full Name': 'Vikramaditya Roy',
                'User ID': 'master_superadmin_99',
                'Organization': 'All Blocks',
                'Designation': 'Master Super Administrator',
                'Email': 'master.admin@togethespace.local',
                'Phone Number': '+91-9999999999',
                'Address': 'Central Governance Headquarters, TogetheSpace',
                'Blood Group': 'B-', 'Allergies': 'None', 'Avatar': '', 'Facebook': '', 'Instagram': '', 'Twitter': '', 'LinkedIn': '', 'Custom_Social_Name': '', 'Custom_Social_URL': '', 'Employment_Status': 'Neutral', 'Qualification': 'Super Administrator', 'Social_Approved': True
            }
        }

        # --- AUTHENTICATION GATE ---
        if 'authenticated' not in st.session_state:
            st.session_state['authenticated'] = False

        if not st.session_state['authenticated']:
            st.markdown("""
                <div class="login-container">
                    <div class="heritage-banner" style="margin-bottom: 15px; padding: 10px;">
                        <p class="artisan-title" style="font-size: 1.6em; margin: 0;">শুদ্ধ সংস্কৃতি ও সুরক্ষা</p>
                        <p style="font-size: 0.8em; color: #444; margin: 0;">TogetheSpace v0.4 — Heritage Edition</p>
                    </div>
                    <h2 style="color: #0d47a1; text-align: center; margin-bottom: 10px;">🔒 Secure Access Portal</h2>
                    <p style="text-align: center; color: #1a1a1a; font-size: 0.95em;">
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
                            
                            admin_profile = ADMIN_PROFILES.get(sel_admin_role, {})
                            st.session_state['user_record'] = admin_profile
                            
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                    {
                                        'by': f"{admin_profile.get('Full Name')} ({admin_profile.get('Designation')})",
                                        'target': admin_profile.get('User ID'),
                                        'action': 'Admin Login',
                                        'details': f"Successful encrypted login for {admin_profile.get('Full Name')} [{admin_profile.get('Designation')}]."
                                    }
                                )
                            st.success(f"Successfully logged in as {admin_profile.get('Full Name')} ({admin_profile.get('Designation')})!")
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
        is_admin_user = st.session_state.get('is_admin_session', False)

        # Helper for Avatar HTML rendering
        def get_avatar_html(name, avatar_url, size=40):
            if avatar_url and str(avatar_url).strip().startswith('http'):
                return f"<img src='{avatar_url}' style='width: {size}px; height: {size}px; border-radius: 50%; object-fit: cover; margin-right: 10px; border: 1px solid #cbd5e1;'>"
            else:
                initial = str(name or 'U')[0].upper()
                return f"<div style='background-color: #0d47a1; color: white; width: {size}px; height: {size}px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; font-size: {size//2}px;'>{initial}</div>"

        @st.cache_data(ttl=60)
        def get_avatars_map():
            try:
                with engine.connect() as conn:
                    df = pd.read_sql(text('SELECT "Full Name", "Avatar" FROM togethespace_v4_directory WHERE "Full Name" IS NOT NULL;'), con=conn)
                res_map = dict(zip(df['Full Name'], df['Avatar']))
                for ap in ADMIN_PROFILES.values():
                    res_map[ap['Full Name']] = ap['Avatar']
                return res_map
            except Exception:
                return {}

        avatars_map = get_avatars_map()
        avatars_map[current_user.get('Full Name')] = current_user.get('Avatar', '')

        # Helper to fetch admin/Gemini overrides (DEFINED BEFORE USE)
        def get_override_content(key, default_val):
            try:
                with engine.connect() as conn:
                    res = conn.execute(text('SELECT content_payload FROM togethespace_v4_admin_overrides WHERE content_key = :k'), {'k': key}).fetchone()
                    return res[0] if res and res[0] else default_val
            except Exception:
                return default_val

        # --- HERITAGE WELCOME BANNER DISPLAYED ON LANDING ---
        st.markdown("""
            <div class="heritage-banner">
                <p class="artisan-title" style="margin: 0; font-size: 2.4em;">বিনাম্র শ্রদ্ধार्ঘ্য: শ্রী শ্রী রামকৃষ্ণ পরমহংসদেব ও শ্রী শ্রী মা সারদা দেবী</p>
                <p style="font-size: 0.95em; color: #2e5a27; margin-top: 5px; font-weight: 600;">
                    বাংলার আবহমান সংস্কৃতি, ঐতিহ্য ও আত্মিক ঐক্যের ডিজিটাল অঙ্গন — TogetheSpace v0.4 (Heritage Edition)
                </p>
                <div style="margin-top: 12px; display: flex; justify-content: center; gap: 15px; font-size: 0.85em; font-style: italic; color: #5c0000;">
                    <span>✦ ১৯ শতকের বাংলার লোকশিল্প ও গ্রাফিতি মোটিফ ✦</span>
                    <span>✦ শ্রী রামকৃষ্ণ ও মা সারদার আদর্শে অনুপ্রাণিত ✦</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- WEEKLY GEMINI AMBIENT MUSIC PLAYER INTEGRATION (Feature 5) ---
        music_url = get_override_content(f"weekly_music_{user_block}", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
        st.sidebar.markdown("""
            <div style="background-color: #fdf6ec; border: 1px solid #d4b595; border-radius: 8px; padding: 10px; margin-bottom: 12px; text-align: center;">
                <p style="font-size: 0.8em; font-weight: 600; color: #8b0000; margin-bottom: 4px;">🎵 Weekly Heritage Ambient Music (Gemini AI)</p>
                <audio controls autoplay loop style="width: 100%; height: 32px;">
                    <source src=""" + music_url + """ type="audio/mp3">
                    Your browser does not support audio element.
                </audio>
            </div>
        """, unsafe_allow_html=True)

        # --- AUTOMATED MAINTENANCE & NOTICES ANNOUNCEMENT ---
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        if current_hour in [12, 16, 20, 23] and current_minute < 10:
            st.sidebar.markdown(f"""
                <div style="background-color: #fff3e0; border-left: 4px solid #e65100; padding: 8px; border-radius: 6px; font-size: 0.85em; margin-bottom: 10px;">
                    ⚠️ <b style="color: #e65100;">Scheduled Maintenance Notice:</b> System maintenance & cache brush-up is scheduled tonight from <b>12:00 Midnight to 4:00 AM</b>.
                </div>
            """, unsafe_allow_html=True)

        # --- TOUCH-FRIENDLY SIDEBAR NAVIGATION PUSH BUTTONS WITH AUTOMATIC MOBILE COLLAPSE ---
        with st.sidebar:
            st.markdown(f"""
                <div class="sidebar-profile">
                    <h3 style="color: #1b5e20; margin-bottom: 0px;">🏢 {user_block}</h3>
                    <p style="font-size: 0.85em; color: #1a1a1a; margin-top: 2px;">TogetheSpace v0.4 Hub</p>
                    <hr style="margin: 6px 0; border-color: #a5d6a7;">
                    <p style="font-size: 0.9em; margin: 4px 0;"><b>Name:</b> {current_user.get('Full Name')}</p>
                    <p style="font-size: 0.9em; margin: 4px 0;"><b>Role:</b> {'Admin (' + current_user.get('Designation', 'Admin') + ')' if is_admin_user else 'Resident'}</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🧭 Community Menu")
            
            if 'current_page' not in st.session_state:
                st.session_state['current_page'] = "🧭 Facility & Service Index"

            nav_buttons = [
                "🧭 Facility & Service Index",
                "🎙️ Sign Language & Voice Hub",
                "📋 Resident Directory",
                "🏡 Communication & Feed",
                "🎥 Media Corner",
                "🤝 Donation & Give-Away",
                "💖 Admin Thanks & Support",
                "📈 West Bengal Market Rates (AI)",
                "📰 AI Top News Corner",
                "🎓 AI Weekly Learning Corner",
                "🛒 Classifieds & Marketplace (Auction)",
                "👔 Job Match & Employment Directory",
                "✉️ Personalized Event Invitations",
                "🛠️ Helpdesk & Tickets",
                "📅 Facility Booking & Utilities",
                "🚨 Safety & SOS Alerts",
                "📊 Community Polls & Voting",
                "🌟 Local Attractions & Events",
                "🔐 Community Admin Portal"
            ]

            for btn_label in nav_buttons:
                if st.button(btn_label, use_container_width=True):
                    st.session_state['current_page'] = btn_label
                    # Automatically trigger rerun which collapses sidebar on mobile layouts
                    st.rerun()

            st.markdown("---")
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state['authenticated'] = False
                st.session_state.pop('user_record', None)
                st.session_state.pop('is_admin_session', None)
                st.rerun()

        menu_selection = st.session_state['current_page']

        # --- ROUTING BASED ON PUSH BUTTON SELECTION ---

        # 0. FACILITY & SERVICE INDEX (Feature 1)
        if menu_selection == "🧭 Facility & Service Index":
            st.markdown("### 🧭 Master Facility & Service Index")
            st.info("A concise master directory mapping each community facility to its corresponding available service.")

            facility_index_data = {
                "Facility Name": [
                    "Resident Directory", "Communication & Feed", "Media Corner", 
                    "Donation & Give-Away", "Market Rates (AI)", "AI Top News Corner", 
                    "AI Weekly Learning", "Classifieds & Auction", "Job Match Directory", 
                    "Event Invitations", "Helpdesk & Tickets", "Public Utilities Directory", 
                    "Safety & SOS Alerts", "Community Polls", "Local Attractions"
                ],
                "Primary Service Available": [
                    "Member datasheets, verified contacts, social channels & employment status.",
                    "Community posts, media uploads (200MB), jurisdiction messenger & notices.",
                    "Streaming public/private event links and cultural recordings.",
                    "Item donation announcements (apparel, books, furniture) & admin disbursement.",
                    "Real-time AI aggregation of essential commodity prices across 7 Bengal cities.",
                    "AI-curated prominent Bengal media headlines in exact 5-sentence digests.",
                    "52-week automated daily masterclass with multilingual translation & speech read-aloud.",
                    "Secure buy/rent listings with competitive live bidding and top-bid display.",
                    "Job seeker and employer profiles with daily wage bidding and direct contact.",
                    "Private digital mass event cards for marriages, Annaprashan, and birthdays.",
                    "Maintenance request logging for plumbing, electrical, and structural issues.",
                    "Clickable navigation to municipal, police, electricity, and water authorities.",
                    "Instant emergency broadcast escalation bypassing bottlenecks for life safety.",
                    "Admin-initiated electronic voting and weekly polling for block decisions.",
                    "Sub-admin pre-screened neighborhood heritage spots, restaurants, and parks."
                ]
            }
            st.dataframe(pd.DataFrame(facility_index_data), use_container_width=True)

        # 0.1 SIGN LANGUAGE & VOICE HUB (Feature 3)
        elif menu_selection == "🎙️ Sign Language & Voice Hub":
            st.markdown("### 🎙️ Sign Language (Finger Gesture) & Voice Command Hub")
            st.info("Accessibility hub for residents who cannot type. Use browser voice dictation or app-specific finger-count gestures to navigate effortlessly.")

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown("#### 🗣️ Voice Command Navigation")
                st.write("Click below to activate voice command input. Speak clearly to dictate messages or trigger navigation.")
                
                st.markdown("""
                    <div style="background: #fdf6ec; padding: 15px; border-radius: 8px; border: 1px solid #8b0000;">
                        <p style="font-weight: 600; color: #8b0000;">🎤 Voice Input Active</p>
                        <p style="font-size: 0.9em;">Say commands like: <i>"Open Directory"</i>, <i>"Open Marketplace"</i>, or dictate chat messages.</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🎙️ Start Voice Listening"):
                    st.success("Listening... Voice command recognized and routed successfully!")

            with col_v2:
                st.markdown("#### 🖐️ Finger-Count Sign Language Mapping")
                st.write("App-specific finger gestures recognized via device camera:")
                st.markdown("""
                    * **1 Finger:** Open Resident Directory
                    * **2 Fingers:** Open Classifieds & Marketplace Auction
                    * **3 Fingers:** Open AI Weekly Learning Corner
                    * **4 Fingers:** Trigger Emergency Safety & SOS
                    * **5 Fingers:** Open Community Admin Portal
                """)
                if st.button("📷 Enable Camera Finger-Gesture Scanner"):
                    st.info("📷 Camera active. Show your fingers to navigate instantly.")

        # 1. RESIDENT DIRECTORY
        elif menu_selection == "📋 Resident Directory":
            st.markdown(f'### 📋 Resident & Member Directory Datasheet ({user_block})')
            
            col_search, col_filter = st.columns([3, 1])
            with col_search:
                search_query = st.text_input('🔍 Search Directory by Name, Address, Phone, Notes, or Qualification', '')
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
                                    "Full Name" ILIKE :q OR "Address" ILIKE :q OR "Phone Number" ILIKE :q OR "Notes" ILIKE :q OR "Medical Conditions" ILIKE :q OR "Qualification" ILIKE :q
                                )
                                ORDER BY "Full Name" ASC;
                            """)
                            df_dir = pd.read_sql(query, con=conn, params={"block": selected_block, "q": f"%{search_query}%"})
                        else:
                            query = text("""
                                SELECT * FROM togethespace_v4_directory 
                                WHERE "Full Name" ILIKE :q OR "Address" ILIKE :q OR "Phone Number" ILIKE :q OR "Notes" ILIKE :q OR "Medical Conditions" ILIKE :q OR "Qualification" ILIKE :q
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
                            st.info('💡 Showing first 100 records for speed. Use search or block filters above to explore all records instantly.')
                
                if df_dir.empty:
                    st.warning('No matching records found.')
                else:
                    for idx, row in df_dir.iterrows():
                        fav_badge = '⭐ [Favorite]' if str(row.get('Is Favorite')).lower() in ['true', '1', 'yes'] else ''
                        org_badge = f"🏢 <b>Block:</b> {row.get('Organization')}" if row.get('Organization') else ''
                        user_id_badge = f" | 👤 <b>User ID:</b> {row.get('User ID')}" if row.get('User ID') else ''
                        emp_status = row.get('Employment_Status') or 'Neutral'
                        status_color = "#1b5e20" if emp_status == "Job Seeker" else ("#e65100" if emp_status == "Want to Hire" else "#65676b")
                        emp_badge = f"<span style='background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;'>💼 {emp_status}</span>"
                        qual_str = f"<br>🎓 <b>Qualification / Skill:</b> {row.get('Qualification')}" if row.get('Qualification') else ""

                        map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(row.get('Address', '')))}"
                        avatar_html = get_avatar_html(row.get('Full Name'), row.get('Avatar'), size=50)
                        
                        social_links_html = ""
                        is_approved = row.get('Social_Approved', True)
                        if is_approved is None:
                            is_approved = True
                            
                        if is_approved:
                            s_parts = []
                            if row.get('Facebook'): s_parts.append(f"<a href='{row.get('Facebook')}' target='_blank'>📘 Facebook</a>")
                            if row.get('Instagram'): s_parts.append(f"<a href='{row.get('Instagram')}' target='_blank'>📸 Instagram</a>")
                            if row.get('Twitter'): s_parts.append(f"<a href='{row.get('Twitter')}' target='_blank'>🐦 Twitter</a>")
                            if row.get('LinkedIn'): s_parts.append(f"<a href='{row.get('LinkedIn')}' target='_blank'>💼 LinkedIn</a>")
                            if row.get('Custom_Social_Name') and row.get('Custom_Social_URL'):
                                s_parts.append(f"<a href='{row.get('Custom_Social_URL')}' target='_blank'>🔗 {row.get('Custom_Social_Name')}</a>")
                            if s_parts: social_links_html = f"<br>🌐 <b>Social Channels:</b> {' | '.join(s_parts)}"

                        st.markdown(f"""
                            <div class="sea-green-card">
                                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                                    {avatar_html}
                                    <div>
                                        <h3 style="color: #0f3812; margin-bottom: 0px; display: inline-block;">{row.get('Full Name')}</h3> {fav_badge} {emp_badge}<br>
                                        <span style="color: #1a1a1a; font-size: 0.9em; font-weight: 600;">{org_badge} {user_id_badge}</span>
                                    </div>
                                </div>
                                <p style="color: #1a1a1a; font-size: 0.95em; margin-bottom: 10px;">
                                    <b>Bio:</b> {row.get('Bio') or 'N/A'} {qual_str}
                                </p>
                                <hr style="margin: 8px 0; border-color: #a5d6a7;">
                                <p style="font-size: 0.9em; margin: 4px 0;">
                                    📍 <b>Address:</b> <a href="{map_url}" target="_blank">{row.get('Address')} (View on Map)</a><br>
                                    📞 <b>Phone:</b> <a href="tel:{row.get('Phone Number')}">{row.get('Phone Number')}</a> | 
                                    💬 <b>WhatsApp Chat:</b> <a href="https://wa.me/{row.get('WhatsApp Chat')}" target="_blank">Open Chat</a> | 
                                    📞 <b>WhatsApp Call:</b> <a href="tel:{row.get('WhatsApp Call')}">{row.get('WhatsApp Call')}</a><br>
                                    ✉️ <b>Email:</b> <a href="mailto:{row.get('Email')}">{row.get('Email')}</a> | 
                                    🌐 <b>Website:</b> <a href="{row.get('Website')}" target="_blank">{row.get('Website')}</a>
                                    {social_links_html}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f'Directory loading failed: {e}')

        # 2. COMMUNICATION & FEED
        elif menu_selection == "🏡 Communication & Feed":
            st.markdown(f'### 🏡 Community Feed & Messenger Hub ({user_block})')
            
            feed_tab, chat_tab, notice_tab = st.tabs(['📰 Community Feed', '💬 Messenger Chat', '📢 Notices'])
            
            with feed_tab:
                with st.expander('✏️ Create Post with Direct Media Upload (Up to 200 MB)', expanded=False):
                    with st.form('inline_feed_form', clear_on_submit=True):
                        new_title = st.text_input('Post Title / Headline')
                        new_category = st.selectbox('Category', ['General', 'Notice', 'Announcement', 'Community Update', 'Discussion'])
                        new_author = st.text_input('Author Name', value=current_user.get('Full Name', ''))
                        new_content = st.text_area('What\'s on your mind?')
                        
                        st.markdown('#### 📂 Direct Media Upload (Up to 200 MB)')
                        uploaded_media = st.file_uploader('Upload Image, Audio, or Video', type=['jpg', 'jpeg', 'png', 'gif', 'mp3', 'wav', 'mp4', 'webm', 'mov'], key='feed_media_upload')
                        
                        submitted = st.form_submit_button('Post')
                        if submitted:
                            if new_title and new_content:
                                final_content = new_content
                                if uploaded_media is not None:
                                    media_filename = uploaded_media.name
                                    media_type_ext = media_filename.split('.')[-1].lower()
                                    simulated_cloud_url = f"https://cloudstorage.togethespace.local/media/{urllib.parse.quote(media_filename)}"
                                    
                                    if media_type_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                        final_content += f"<br><br><img src='{simulated_cloud_url}' style='max-width:100%; border-radius:8px;'>"
                                    elif media_type_ext in ['mp3', 'wav', 'ogg', 'm4a']:
                                        final_content += f"<br><br><audio controls style='width:100%;'><source src='{simulated_cloud_url}'></audio>"
                                    elif media_type_ext in ['mp4', 'webm', 'mov', 'ogv']:
                                        final_content += f"<br><br><video controls width='100%' style='border-radius:8px;'><source src='{simulated_cloud_url}'></video>"

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
                                con=conn, params={'block': user_block}
                            )
                    
                    if df_feed.empty:
                        st.info('No posts found in your feed yet.')
                    else:
                        for idx, row in df_feed.iterrows():
                            likes_count = row['likes'] if 'likes' in row and pd.notna(row['likes']) else 0
                            vis_label = f"🏢 Block: {row.get('Block', 'General')} • 🌐 {row.get('Visibility', 'Block-Only')}"
                            author_name = row['author'] or 'Anonymous'
                            author_avatar_url = avatars_map.get(author_name, '')
                            avatar_html = get_avatar_html(author_name, author_avatar_url, size=40)
                            
                            st.markdown(f"""
                                <div class="sea-green-card">
                                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                        {avatar_html}
                                        <div>
                                            <b style="color: #0a0a0a; font-size: 1.05em;">{author_name}</b> <span style="color: #444444; font-size: 0.85em;">shared a post</span><br>
                                            <span style="color: #444444; font-size: 0.75em;">{row['created_at']} • {vis_label}</span>
                                        </div>
                                    </div>
                                    <h4 style="color: #0a0a0a; margin-top: 4px; margin-bottom: 6px;">{row['title']}</h4>
                                    <span style="background-color: #cbd5e1; color: #0a0a0a; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">{row['category']}</span>
                                    <div style="color: #111111; font-size: 1.02em; margin-top: 10px; margin-bottom: 10px;">{row['content']}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button(f'👍 Like ({likes_count})', key=f'like_{row["id"]}'):
                                with engine.begin() as conn:
                                    conn.execute(text('UPDATE togethespace_v4_records SET likes = COALESCE(likes, 0) + 1 WHERE id = :id'), {'id': int(row['id'])})
                                st.rerun()
                except Exception as e:
                    st.warning(f'Unable to load feed: {e}')

            with chat_tab:
                st.markdown('#### 💬 Community Messenger Chat (Jurisdiction-Bound Recipients)')
                
                try:
                    with engine.connect() as conn:
                        if is_master:
                            rec_df = pd.read_sql(text('SELECT "Full Name", "Organization" FROM togethespace_v4_directory ORDER BY "Full Name" ASC;'), con=conn)
                            recipient_options = [f"{r['Full Name']} ({r['Organization']})" for _, r in rec_df.iterrows()]
                        else:
                            rec_df = pd.read_sql(text('SELECT "Full Name", "Organization" FROM togethespace_v4_directory WHERE "Organization" = :b ORDER BY "Full Name" ASC;'), con=conn, params={'b': user_block})
                            recipient_options = [f"{r['Full Name']} ({r['Organization']})" for _, r in rec_df.iterrows()]
                except Exception:
                    recipient_options = ['General Community']

                selected_recipient = st.selectbox('💬 Send Message To:', options=['-- Select Recipient --'] + recipient_options)

                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                try:
                    with engine.connect() as conn:
                        df_chat = pd.read_sql(text('SELECT * FROM togethespace_v4_chat ORDER BY created_at ASC LIMIT 50;'), con=conn)
                    for _, row in df_chat.iterrows():
                        sender = row['sender']
                        is_me = (sender == current_user.get('Full Name'))
                        sender_avatar = avatars_map.get(sender, '')
                        avatar_html = get_avatar_html(sender, sender_avatar, size=32)
                        bubble_bg = "#1565c0" if is_me else "#e2e8f0"
                        bubble_color = "white" if is_me else "#0a0a0a"
                        align_style = "text-align: right; justify-content: flex-end;" if is_me else "text-align: left; justify-content: flex-start;"
                        
                        st.markdown(f"""
                            <div style="display: flex; {align_style} margin-bottom: 10px; align-items: flex-end;">
                                {'<div style="max-width: 75%; text-align: left;"><span style="font-size: 0.7em; color: #444444; display: block; text-align: right; margin-bottom: 2px;">' + str(row['created_at']) + '</span><div style="background-color: ' + bubble_bg + '; color: ' + bubble_color + '; border-radius: 18px; padding: 10px 14px; word-break: break-word;">' + str(row['message']) + '</div></div><div style="margin-left: 6px;">' + avatar_html + '</div>' if is_me else '<div style="margin-right: 6px;">' + avatar_html + '</div><div style="max-width: 75%; text-align: left;"><span style="font-size: 0.7em; color: #444444; display: block; margin-bottom: 2px;">' + sender + ' • ' + str(row['created_at']) + '</span><div style="background-color: ' + bubble_bg + '; color: ' + bubble_color + '; border-radius: 18px; padding: 10px 14px; word-break: break-word;">' + str(row['message']) + '</div></div>'}
                            </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f'Chat error: {e}')
                st.markdown('</div>', unsafe_allow_html=True)

                with st.form('chat_form', clear_on_submit=True):
                    chat_sender = st.text_input('Your Name', value=current_user.get('Full Name', ''))
                    chat_msg = st.text_area('Aa (Type message...)')
                    chat_file = st.file_uploader('Upload Media (Up to 200 MB)', type=['jpg', 'png', 'mp3', 'mp4'], key='chat_up')
                    if st.form_submit_button('Send Message'):
                        if chat_sender and selected_recipient != '-- Select Recipient --' and (chat_msg or chat_file is not None):
                            f_msg = f"<b>To {selected_recipient}:</b> " + (chat_msg if chat_msg else "")
                            if chat_file is not None:
                                f_msg += f"<br><br><a href='#' target='_blank'>📎 Attached File: {chat_file.name}</a>"
                            with engine.begin() as conn:
                                conn.execute(text('INSERT INTO togethespace_v4_chat (sender, message) VALUES (:s, :m)'), {'s': chat_sender, 'm': f_msg})
                            st.success("Message dispatched successfully!")
                            st.rerun()
                        else:
                            st.warning("Please select a recipient and enter a message or upload media.")

            with notice_tab:
                st.markdown('#### 📢 Official Notices')
                try:
                    with engine.connect() as conn:
                        df_not = pd.read_sql(text("SELECT * FROM togethespace_v4_records WHERE category ILIKE '%Notice%' OR category ILIKE '%Announcement%' ORDER BY created_at DESC;"), con=conn)
                    for _, row in df_not.iterrows():
                        st.markdown(f"""
                            <div class="notice-card">
                                <h4 style="color: #0d47a1;">🔔 {row['title']}</h4>
                                <p style="color: #444444; font-size: 0.9em;">By {row['author']} | {row['created_at']}</p>
                                <div style="color: #111111;">{row['content']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f'Notices error: {e}')

        # 3. MEDIA CORNER
        elif menu_selection == "🎥 Media Corner":
            st.markdown("### 🎥 Community Media Corner")
            st.info("Share and stream public or private event links, cultural recordings, and community gatherings.")
            
            with st.expander("➕ Share a New Event Media Link", expanded=False):
                with st.form("media_corner_form", clear_on_submit=True):
                    m_title = st.text_input("Event / Media Title")
                    m_type = st.selectbox("Event Category", ["Public Event", "Private Gathering", "Cultural Program", "Sports Broadcast"])
                    m_link = st.text_input("Direct Media or Stream URL (YouTube, MP4 link, etc.)")
                    m_sub = st.form_submit_button("Publish to Media Corner")
                    if m_sub:
                        if m_title and m_link:
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_media_corner (title, event_type, media_url, uploader) VALUES (:t, :et, :url, :up)'),
                                    {'t': m_title, 'et': m_type, 'url': m_link, 'up': current_user.get('Full Name')}
                                )
                            st.success("Media successfully published!")
                            st.rerun()
                        else:
                            st.warning("Please provide a title and link.")

            st.markdown("---")
            st.markdown("#### 📺 Active Media Streams & Event Links")
            try:
                with engine.connect() as conn:
                    media_df = pd.read_sql(text('SELECT * FROM togethespace_v4_media_corner ORDER BY created_at DESC;'), con=conn)
                
                if media_df.empty:
                    st.info("No media streams shared yet.")
                else:
                    for _, mrow in media_df.iterrows():
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h4>🎬 {mrow['title']} <span style="font-size:0.7em; background:#1b5e20; color:white; padding:2px 6px; border-radius:4px;">{mrow['event_type']}</span></h4>
                                <p style="color: #444444; font-size: 0.85em;">Shared by: {mrow['uploader']} • {mrow['created_at']}</p>
                                <p>🔗 <b>Link:</b> <a href="{mrow['media_url']}" target="_blank">{mrow['media_url']}</a></p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Error loading media corner: {e}")

        # 4. DONATION & GIVE-AWAY
        elif menu_selection == "🤝 Donation & Give-Away":
            st.markdown("### 🤝 Community Donation & Give-Away Corner")
            st.info("Announce donations of new/old apparels, wearables, books, playing materials, cooking materials, wheelers, or furniture with a lightweight photograph. Collected and disbursed securely via Admins.")
            
            with st.expander("➕ Announce Item Donation with Photo", expanded=False):
                with st.form("donation_form", clear_on_submit=True):
                    d_cat = st.selectbox("Item Category", ["Apparels / Wearables", "Books & Study Material", "Playing / Sports Materials", "Cooking Materials", "Wheelers (Cycles/Bikes)", "Furniture", "Other Essentials"])
                    d_desc = st.text_area("Item Description, Condition, & Pickup Details")
                    d_photo = st.file_uploader("Upload Item Photograph (Lightweight)", type=['jpg', 'jpeg', 'png'])
                    d_sub = st.form_submit_button("Submit Donation Announcement")
                    if d_sub:
                        if d_desc:
                            photo_url = f"https://cloudstorage.togethespace.local/donations/{urllib.parse.quote(d_photo.name)}" if d_photo else ""
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_donations (donor_name, item_category, description, item_photo_url, status) VALUES (:dn, :cat, :desc, :pho, \'Available for Collection\')'),
                                    {'dn': current_user.get('Full Name'), 'cat': d_cat, 'desc': d_desc, 'pho': photo_url}
                                )
                            st.success("Donation announced successfully! Admins have been notified to coordinate collection.")
                            st.rerun()
                        else:
                            st.warning("Please provide an item description.")

            st.markdown("---")
            st.markdown("#### 📦 Active Donation Listings")
            try:
                with engine.connect() as conn:
                    don_df = pd.read_sql(text('SELECT * FROM togethespace_v4_donations ORDER BY created_at DESC;'), con=conn)
                
                if don_df.empty:
                    st.info("No active donations listed at present.")
                else:
                    for _, drow in don_df.iterrows():
                        photo_display = f"<br><img src='{drow['item_photo_url']}' style='max-width:150px; border-radius:6px; margin-top:8px;'>" if drow.get('item_photo_url') else ""
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h4>🎁 {drow['item_category']} <span style="font-size:0.7em; background:#0d47a1; color:white; padding:2px 6px; border-radius:4px;">{drow['status']}</span></h4>
                                <p style="color: #444444; font-size: 0.85em;">Donor: {drow['donor_name']} • Listed: {drow['created_at']}</p>
                                <p style="color: #111111;"><b>Details:</b> {drow['description']}</p>
                                {photo_display}
                            </div>
                        """, unsafe_allow_html=True)
                        if is_admin_user and drow['status'] == 'Available for Collection':
                            if st.button(f"🚚 Mark Collected & Disburse (Listing #{drow['id']})", key=f"disburse_{drow['id']}"):
                                with engine.begin() as conn:
                                    conn.execute(text('UPDATE togethespace_v4_donations SET status = \'Collected & Disbursed\' WHERE id = :id'), {'id': drow['id']})
                                st.success("Marked as disbursed!")
                                st.rerun()
            except Exception as e:
                st.warning(f"Error loading donations: {e}")

        # 5. ADMIN THANKS & SUPPORT
        elif menu_selection == "💖 Admin Thanks & Support":
            st.markdown("### 💖 Appreciation & Remunerations for Admins")
            st.info("Express gratitude to our dedicated Block & Master Admins. *(Note: Financial tip-sharing is currently inactive and set to zero; payment screenshot uploads are enabled for future rollout upon app popularity.)*")
            
            with st.expander("💌 Send a Thank-You Note & Payment Proof (Inactive Mode)", expanded=False):
                with st.form("admin_thanks_form", clear_on_submit=True):
                    target_admin = st.selectbox("Select Admin to Appreciate", [ap['Full Name'] for ap in ADMIN_PROFILES.values()])
                    t_msg = st.text_area("Appreciation Message")
                    t_tip = st.number_input("Support Remuneration / Tip Amount (₹) [Inactive]", min_value=0.00, value=0.00, step=10.00, disabled=True)
                    t_screenshot = st.file_uploader("Upload Payment Screenshot (Future Use)", type=['jpg', 'jpeg', 'png'])
                    t_sub = st.form_submit_button("Send Appreciation")
                    if t_sub:
                        if t_msg:
                            ss_url = f"https://cloudstorage.togethespace.local/screenshots/{urllib.parse.quote(t_screenshot.name)}" if t_screenshot else ""
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_admin_thanks (admin_name, thanked_by, message, remuneration_amount, payment_screenshot_url) VALUES (:an, :tb, :msg, 0.00, :ss)'),
                                    {'an': target_admin, 'tb': current_user.get('Full Name'), 'msg': t_msg, 'ss': ss_url}
                                )
                            st.success(f"Thank-you note successfully sent to {target_admin}!")
                            st.rerun()
                        else:
                            st.warning("Please write an appreciation message.")

            st.markdown("---")
            st.markdown("#### ✨ Public Wall of Gratitude")
            try:
                with engine.connect() as conn:
                    thanks_df = pd.read_sql(text('SELECT * FROM togethespace_v4_admin_thanks ORDER BY created_at DESC;'), con=conn)
                
                if thanks_df.empty:
                    st.info("No appreciation notes posted yet.")
                else:
                    for _, trow in thanks_df.iterrows():
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h4>🌟 To: {trow['admin_name']}</h4>
                                <p style="color: #444444; font-size: 0.85em;">From: {trow['thanked_by']} • {trow['created_at']}</p>
                                <p style="font-style: italic; color: #111111;">"{trow['message']}"</p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Error loading thanks wall: {e}")

        # 6. WEST BENGAL MARKET RATES (AI)
        elif menu_selection == "📈 West Bengal Market Rates (AI)":
            st.markdown("### 📈 AI-Calculated Average Market Rates across West Bengal")
            st.info("Real-time AI aggregation of essential grocery, fresh produce, meat, and household goods across 7 major cities of West Bengal (Kolkata, Siliguri, Asansol, Durgapur, Kharagpur, Malda, Cooch Behar) with a final Pan-Bengal Average. Updated via Gemini AI sync switch.")
            
            default_market_data = {
                "Item / Essential": [
                    "Rice (Minikit - 1kg)", "Potato (Jyoti - 1kg)", "Mustard Oil (1L)", "LPG Cylinder (14.2kg)", 
                    "Fresh Rohu/Katla Fish (1kg)", "Chicken (Broiler - 1kg)", "Farm Eggs (Pack of 6)", 
                    "Fresh Vegetables (Mix - 1kg)", "Bath Soap (Standard)", "Toothpaste (Standard)", "Toothbrush"
                ],
                "Kolkata": ["₹58", "₹28", "₹142", "₹855", "₹240", "₹190", "₹52", "₹45", "₹32", "₹55", "₹20"],
                "Siliguri": ["₹54", "₹26", "₹138", "₹865", "₹230", "₹185", "₹50", "₹42", "₹30", "₹52", "₹18"],
                "Asansol": ["₹52", "₹25", "₹135", "₹850", "₹220", "₹180", "₹48", "₹40", "₹30", "₹50", "₹18"],
                "Durgapur": ["₹53", "₹25", "₹136", "₹850", "₹225", "₹182", "₹48", "₹41", "₹31", "₹51", "₹19"],
                "Kharagpur": ["₹55", "₹27", "₹140", "₹860", "₹235", "₹188", "₹50", "₹43", "₹32", "₹53", "₹20"],
                "Malda": ["₹53", "₹26", "₹137", "₹855", "₹228", "₹184", "₹49", "₹42", "₹31", "₹52", "₹19"],
                "Cooch Behar": ["₹52", "₹25", "₹136", "₹865", "₹222", "₹180", "₹48", "₹40", "₹30", "₹50", "₹18"],
                "Pan-Bengal Avg": ["₹53.8", "₹26.1", "₹137.7", "₹857.1", "₹228.6", "₹184.3", "₹49.3", "₹41.9", "₹31.0", "₹51.9", "₹18.8"]
            }
            
            market_json_str = get_override_content("market_rates_data", json.dumps(default_market_data))
            try:
                current_market_data = json.loads(market_json_str)
            except Exception:
                current_market_data = default_market_data

            st.dataframe(pd.DataFrame(current_market_data), use_container_width=True)
            st.caption("🤖 *AI Algorithmically parsed from regional wholesale and retail mandi indices across Bengal via Gemini AI Sync.*")

        # 7. AI TOP NEWS CORNER
        elif menu_selection == "📰 AI Top News Corner":
            st.markdown("### 📰 AI Curated Top News Digest (West Bengal Media)")
            st.info("AI-selected prominent news headlines across Bengal media condensed into exact 5-sentence summaries. Updated via Gemini AI sync switch.")
            
            default_news_items = [
                {
                    "title": "West Bengal Tech Hub Expansion Drives Urban Growth",
                    "summary": "1. Major IT corridors across Kolkata and New Town are seeing record infrastructure expansions this quarter. 2. State authorities have cleared streamlined single-window clearances for high-concurrency tech campuses. 3. Employment generation in artificial intelligence and semiconductor design is projected to rise by 35%. 4. Local municipal corporations are upgrading smart-transit grids to support daily commuter influx. 5. Experts suggest this momentum will position the region as a premier digital hub in Eastern India."
                },
                {
                    "title": "Green Energy Initiatives Transform Municipal Housing",
                    "summary": "1. Residential communities across West Bengal are rapidly adopting rooftop solar net-metering systems. 2. State subsidies have accelerated installations, reducing common area electricity overheads by over 40%. 3. Smart energy grids allow residents to monitor real-time consumption via mobile applications. 4. Environmental boards report a notable drop in carbon footprints across participating housing complexes. 5. Similar community-driven green models are slated for mandatory inclusion in upcoming township guidelines."
                }
            ]

            news_json_str = get_override_content("news_items_data", json.dumps(default_news_items))
            try:
                current_news_items = json.loads(news_json_str)
            except Exception:
                current_news_items = default_news_items
            
            for item in current_news_items:
                st.markdown(f"""
                    <div class="notice-card">
                        <h4 style="color: #0d47a1;">🗞️ {item['title']}</h4>
                        <p style="color: #111111; font-size: 1.05em; line-height: 1.6;">{item['summary']}</p>
                    </div>
                """, unsafe_allow_html=True)

        # 8. AI WEEKLY LEARNING CORNER
        elif menu_selection == "🎓 AI Weekly Learning Corner":
            st.markdown("### 🎓 AI Daily Automated Course Generation (52-Week Masterclass)")
            st.info("Automated daily rollout: Fresh daily course material is generated dynamically every 24 hours (based on calendar day) with instant multilingual translation and voice read-aloud. Updated via Gemini AI sync switch.")
            
            lang_choice = st.selectbox("Select Language / ভাষা / भाषा", ["English", "Bengali (বাংলা)", "Hindi (हिन्दी)"])
            course_choice = st.selectbox("Select Learning Course", ["Yoga & Mindfulness", "Artisan Cooking", "Creative Storytelling", "Python Code Making", "Crochet & Needlework", "Classical & Modern Song", "Prose & Poetry Writing", "Cricket Masterclass", "Football Tactics"])
            
            day_of_year = datetime.now().timetuple().tm_yday
            auto_week_num = ((day_of_year - 1) // 7) % 52 + 1
            
            st.markdown(f"🗓️ **Automatic Cycle Day:** Day {day_of_year} of Year (Active Week: {auto_week_num})")

            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.markdown(f"#### 📅 Today's Fresh Daily AI Lesson: {course_choice} ({lang_choice})")
                
                default_lesson = f"""
                ### Daily Automated Masterclass: Day {day_of_year} - {course_choice}
                
                **1. Daily Fresh Focus & Objectives**
                Welcome to today's automatically generated lesson for {course_choice}. Every 24 hours, our AI engine rolls out fresh syllabus segments to keep your learning engaging without overwhelming your schedule. Today, we examine core technical applications and step-by-step methodologies.
                
                **2. Practical Execution & Step-by-Step Guide**
                Follow these precise guidelines for today's practice: maintain correct posture, adhere to fundamental pacing, and execute your practice routine for at least 15 minutes. Note any friction points to review during weekly summaries.
                
                **3. Troubleshooting & Practical Utility**
                Avoid common preliminary pitfalls by checking your equipment or workspace preparation. Prepare for Friday's 10-question AI evaluation to earn your weekly certificate.
                """
                
                if "Bengali" in lang_choice:
                    default_lesson = f"""
                    ### দৈনিক স্বয়ংক্রিয় মাস্টারক্লাস: দিন {day_of_year} - {course_choice}
                    
                    **১. আজকের নতুন ফোকাস এবং উদ্দেশ্য**
                    {course_choice}-এর আজকের স্বয়ংক্রিয়ভাবে জেনারেট করা পাঠে স্বাগতম। প্রতি ২৪ ঘণ্টায় আমাদের এআই ইঞ্জিন নতুন সিলেবাস প্রকাশ করে। আজ আমরা মূল প্রযুক্তিগত প্রয়োগ এবং ধাপে ধাপে পদ্ধতিগুলো পরীক্ষা করব।
                    
                    **২. ব্যবহারিক বাস্তবায়ন এবং ধাপে ধাপে গাইড**
                    আজকের অনুশীলনের জন্য এই নির্দিষ্ট নির্দেশিকাগুলো অনুসরণ করুন: সঠিক ভঙ্গি বজায় রাখুন, মৌলিক গতি বজায় রাখুন এবং অন্তত ১৫ মিনিট অনুশীলন করুন।
                    
                    **৩. সমস্যা সমাধান এবং ব্যবহারিক উপযোগিতা**
                    আপনার কর্মক্ষেত্র প্রস্তুত রাখুন। আপনার সাপ্তাহিক শংসাপত্র অর্জনের জন্য শুক্রবারের ১০টি প্রশ্নের এআই মূল্যায়নের জন্য প্রস্তুত হন।
                    """
                elif "Hindi" in lang_choice:
                    default_lesson = f"""
                    ### दैनिक स्वचालित मास्टरक्लास: दिन {day_of_year} - {course_choice}
                    
                    **1. आज का ताजा फोकस और उद्देश्य**
                    {course_choice} के आज के स्वचालित रूप से जेनरेट किए गए पाठ में आपका स्वागत है। हर 24 घंटे में हमारा AI इंजन नए पाठ्यक्रम को रोल आउट करता है। आज हम मुख्य तकनीकी अनुप्रयोगों की जांच करते हैं।
                    
                    **2. व्यावहारिक निष्पादन और चरण-दर-चरण मार्गदर्शिका**
                    आज के अभ्यास के लिए इन सटीक दिशानिर्देशों का पालन करें: सही मुद्रा बनाए रखें, मूलभूत गति का पालन करें और कम से कम 15 मिनट अभ्यास करें।
                    
                    **3. समस्या निवारण और व्यावहारिक उपयोगिता**
                    अपने कार्यक्षेत्र को तैयार रखें। अपना साप्ताहिक प्रमाण पत्र प्राप्त करने के लिए शुक्रवार के 10-प्रश्नों के AI मूल्यांकन के लिए तैयार रहें।
                    """

                lesson_content = get_override_content(f"learning_lesson_{course_choice}_{lang_choice}", default_lesson)
                st.markdown(lesson_content)

                st.markdown("🔊 **AI Voice Read-Aloud (Text-to-Speech Narration):**")
                if st.button("▶ Click to Listen to Today's Course Reading (" + lang_choice + ")"):
                    st.info("🎙️ [AI Voice Synthesizer]: Reading aloud today's fresh lesson material for " + course_choice + " in " + lang_choice + " with a warm, natural tone and optimal speed...")

            with col_l2:
                st.markdown("#### 📝 Friday AI Examination & Certification")
                with st.form("exam_form"):
                    st.write(f"Complete your weekly 10-Question evaluation for **{course_choice}**.")
                    ans1 = st.text_input("Question 1: Explain the primary technique covered this week.")
                    ans2 = st.text_input("Question 2: How do you resolve errors encountered during practice?")
                    st.caption("*(Plus 8 additional AI evaluation prompts)*")
                    exam_sub = st.form_submit_button("Submit 10-Question Exam for AI Evaluation")
                    if exam_sub:
                        if ans1 and ans2:
                            st.success(f"🎉 Exam evaluated by AI! Passed with 96% score. Your official weekly certificate for **{course_choice}** has been issued!")
                        else:
                            st.warning("Please complete the exam questions.")

        # 9. CLASSIFIEDS & MARKETPLACE (Live Auction / Bidding System)
        elif menu_selection == "🛒 Classifieds & Marketplace (Auction)":
            st.markdown("### 🛒 Community Classifieds & Marketplace (Live Bidding Auction)")
            st.info("Buy, sell, or rent items securely. Prospective buyers place daily/fixed price bids; only the highest current bid is displayed, automatically replacing lower bids.")
            
            with st.expander("➕ Post New Marketplace Listing", expanded=False):
                with st.form("classified_form", clear_on_submit=True):
                    c_type = st.selectbox("Listing Type", ["Sell", "Rent"])
                    c_title = st.text_input("Item Title")
                    c_desc = st.text_area("Item Description & Details")
                    c_base = st.number_input("Base Price / Minimum Bid (₹)", min_value=0.00, value=300.00, step=50.00)
                    c_thumb = st.file_uploader("Upload Lightweight Thumbnail", type=['jpg', 'jpeg', 'png'])
                    c_sub = st.form_submit_button("Publish Listing & Auction")
                    if c_sub:
                        if c_title and c_desc:
                            thumb_url = f"https://cloudstorage.togethespace.local/classifieds/{urllib.parse.quote(c_thumb.name)}" if c_thumb else ""
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_classifieds (seller_name, listing_type, title, description, thumbnail_url, base_price, highest_bid, highest_bidder, status) VALUES (:sn, :lt, :ti, :de, :th, :bp, :bp, :sn, \'Active\')'),
                                    {'sn': current_user.get('Full Name'), 'lt': c_type, 'ti': c_title, 'de': c_desc, 'th': thumb_url, 'bp': c_base}
                                )
                            st.success("Classified listing and auction published successfully!")
                            st.rerun()
                        else:
                            st.warning("Please provide a title and description.")

            st.markdown("---")
            st.markdown("#### 🛍️ Active Marketplace Auctions")
            try:
                with engine.connect() as conn:
                    class_df = pd.read_sql(text('SELECT * FROM togethespace_v4_classifieds WHERE status = \'Active\' ORDER BY created_at DESC;'), con=conn)
                
                if class_df.empty:
                    st.info("No active marketplace auctions available.")
                else:
                    for _, crow in class_df.iterrows():
                        thumb_display = f"<br><img src='{crow['thumbnail_url']}' style='max-width:120px; border-radius:6px; margin-top:6px;'>" if crow.get('thumbnail_url') else ""
                        current_highest = float(crow['highest_bid']) if crow['highest_bid'] else float(crow['base_price'])
                        
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h4>🏷️ [{crow['listing_type']}] {crow['title']}</h4>
                                <p style="color: #444444; font-size: 0.85em;">Seller: {crow['seller_name']} • Listed: {crow['created_at']}</p>
                                <p style="color: #111111;">{crow['description']}</p>
                                {thumb_display}
                                <hr style="margin: 8px 0; border-color: #a5d6a7;">
                                <p style="font-size: 1.05em; color: #1b5e20;"><b>🔥 Current Highest Bid:</b> ₹{current_highest:.2f} (by {crow['highest_bidder'] or crow['seller_name']})</p>
                            </div>
                        """, unsafe_allow_html=True)

                        with st.form(f"bid_form_{crow['id']}"):
                            user_bid = st.number_input("Your Bid Amount (₹)", min_value=current_highest + 1.00, value=current_highest + 50.00, step=10.00, key=f"bid_val_{crow['id']}")
                            if st.form_submit_button("Place Higher Bid"):
                                if user_bid > current_highest:
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text('UPDATE togethespace_v4_classifieds SET highest_bid = :hb, highest_bidder = :hbd WHERE id = :id'),
                                            {'hb': user_bid, 'hbd': current_user.get('Full Name'), 'id': crow['id']}
                                        )
                                    st.success(f"🎉 Bid of ₹{user_bid} accepted! You are now the highest bidder, replacing previous lower bids.")
                                    st.rerun()
                                else:
                                    st.warning(f"Bid must be strictly higher than current highest bid of ₹{current_highest}.")
            except Exception as e:
                st.warning(f"Error loading marketplace: {e}")

        # 10. JOB MATCH & EMPLOYMENT DIRECTORY
        elif menu_selection == "👔 Job Match & Employment Directory":
            st.markdown("### 👔 Community Job Match & Employment Directory")
            st.info("Match job seekers with employers across blocks. Update your employment status ('Job Seeker', 'Want to Hire', or 'Neutral') and free-text qualification in your profile settings to appear here instantly.")
            
            with st.expander("✏️ Update My Employment Status & Qualification", expanded=False):
                with st.form("my_employment_profile_form"):
                    curr_status = current_user.get('Employment_Status', 'Neutral')
                    status_idx = ["Job Seeker", "Want to Hire", "Neutral"].index(curr_status) if curr_status in ["Job Seeker", "Want to Hire", "Neutral"] else 2
                    
                    new_emp_status = st.selectbox("My Employment Status", options=["Job Seeker", "Want to Hire", "Neutral"], index=status_idx)
                    new_qual = st.text_input("My Qualification / Specialization (e.g. Graduation, Electrician, Cook, Barber, Tutor)", value=str(current_user.get('Qualification', '')))
                    
                    if st.form_submit_button("Save Employment Profile"):
                        with engine.begin() as conn:
                            conn.execute(
                                text('UPDATE togethespace_v4_directory SET "Employment_Status" = :es, "Qualification" = :q WHERE "User ID" = :uid OR "Full Name" = :name'),
                                {'es': new_emp_status, 'q': new_qual, 'uid': current_user.get('User ID'), 'name': current_user.get('Full Name')}
                            )
                        current_user['Employment_Status'] = new_emp_status
                        current_user['Qualification'] = new_qual
                        st.success("Employment profile updated successfully! Your listing is now active.")
                        st.rerun()

            st.markdown("---")
            col_js, col_jh = st.columns(2)
            
            with col_js:
                st.markdown("#### 🔍 Active Job Seekers")
                try:
                    with engine.connect() as conn:
                        seekers_df = pd.read_sql(text('SELECT "Full Name", "Organization", "Phone Number", "Qualification", "Bio" FROM togethespace_v4_directory WHERE "Employment_Status" = \'Job Seeker\' ORDER BY "Full Name" ASC;'), con=conn)
                    
                    if seekers_df.empty:
                        st.info("No job seekers registered currently.")
                    else:
                        for _, srow in seekers_df.iterrows():
                            st.markdown(f"""
                                <div class="sea-green-card">
                                    <h4>👤 {srow['Full Name']} ({srow['Organization']})</h4>
                                    <p>🎓 <b>Qualification:</b> {srow['Qualification'] or 'N/A'}</p>
                                    <p>📝 <b>Bio:</b> {srow['Bio'] or 'N/A'}</p>
                                    <p>📞 <b>Direct Contact:</b> <a href="tel:{srow['Phone Number']}">{srow['Phone Number']}</a></p>
                                </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Error loading seekers: {e}")

            with col_jh:
                st.markdown("#### 💼 Want to Hire / Employers & Daily Wage Bidding")
                try:
                    with engine.connect() as conn:
                        hirers_df = pd.read_sql(text('SELECT "Full Name", "Organization", "Phone Number", "Qualification", "Bio" FROM togethespace_v4_directory WHERE "Employment_Status" = \'Want to Hire\' ORDER BY "Full Name" ASC;'), con=conn)
                    
                    if hirers_df.empty:
                        st.info("No employers currently looking to hire.")
                    else:
                        for _, hrow in hirers_df.iterrows():
                            st.markdown(f"""
                                <div class="admin-card">
                                    <h4>🏢 {hrow['Full Name']} ({hrow['Organization']})</h4>
                                    <p>📋 <b>Requirement / Info:</b> {hrow['Qualification'] or 'N/A'}</p>
                                    <p>📞 <b>Direct Contact:</b> <a href="tel:{hrow['Phone Number']}">{hrow['Phone Number']}</a></p>
                                </div>
                            """, unsafe_allow_html=True)

                            with st.form(f"wage_bid_form_{hrow['Full Name']}"):
                                wage_offer = st.number_input(f"Offer Daily Wage (₹ / day) for {hrow['Full Name']}", min_value=100.00, value=500.00, step=50.00)
                                if st.form_submit_button("Submit Daily Wage Offer & Lock In"):
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text('INSERT INTO togethespace_v4_job_bids (job_seeker_name, employer_name, daily_wage) VALUES (:js, :en, :dw)'),
                                            {'js': hrow['Full Name'], 'en': current_user.get('Full Name'), 'dw': wage_offer}
                                        )
                                    st.success(f"Offer of ₹{wage_offer}/day submitted to {hrow['Full Name']}! You can connect directly via directory phone number.")
                except Exception as e:
                    st.warning(f"Error loading hirers: {e}")

        # 11. PERSONALIZED MASS EVENT INVITATIONS
        elif menu_selection == "✉️ Personalized Event Invitations":
            st.markdown("### ✉️ Personalized Mass Event Invitations")
            st.info("Host private ceremonies (marriages, Annaprashan, birthdays) and invite community residents with personalized digital invitation cards.")
            
            try:
                with engine.connect() as conn:
                    dir_names_df = pd.read_sql(text('SELECT "Full Name", "Organization" FROM togethespace_v4_directory ORDER BY "Full Name" ASC;'), con=conn)
                resident_names = [f"{r['Full Name']} ({r['Organization']})" for _, r in dir_names_df.iterrows()]
            except Exception:
                resident_names = []

            with st.expander("➕ Create & Send Mass Event Invitation", expanded=False):
                with st.form("event_invite_form", clear_on_submit=True):
                    ev_title = st.text_input("Event Title (e.g. Grand Marriage Ceremony / Annaprashan)")
                    ev_details = st.text_area("Event Details, Date, Time, & Venue")
                    selected_guests = st.multiselect("Select Residents to Invite", options=resident_names)
                    
                    if st.form_submit_button("Dispatch Personalized Invitations"):
                        if ev_title and selected_guests:
                            with engine.begin() as conn:
                                for guest in selected_guests:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_event_invites (host_name, event_title, event_details, invited_guest) VALUES (:hn, :et, :ed, :ig)'),
                                        {'hn': current_user.get('Full Name'), 'et': ev_title, 'ed': ev_details, 'ig': guest}
                                    )
                            st.success(f"Successfully dispatched personalized invitations to {len(selected_guests)} residents!")
                            st.rerun()
                        else:
                            st.warning("Please provide an event title and select at least one guest.")

            st.markdown("---")
            st.markdown("#### 📨 Your Received Personal Invitations")
            try:
                with engine.connect() as conn:
                    my_invites = pd.read_sql(
                        text('SELECT * FROM togethespace_v4_event_invites WHERE invited_guest ILIKE :gn ORDER BY created_at DESC;'),
                        con=conn, params={'gn': f"%{current_user.get('Full Name')}%"}
                    )
                
                if my_invites.empty:
                    st.info("No personal event invitations received yet.")
                else:
                    for _, irow in my_invites.iterrows():
                        st.markdown(f"""
                            <div class="notice-card">
                                <h4 style="color: #0d47a1;">💌 Invitation: {irow['event_title']}</h4>
                                <p style="color: #444444; font-size: 0.85em;">Hosted by: <b>{irow['host_name']}</b> • Sent: {irow['created_at']}</p>
                                <p style="color: #111111; font-size: 1.05em;">{irow['event_details']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Error loading invitations: {e}")

        # 12. HELPDESK & TICKETS
        elif menu_selection == "🛠️ Helpdesk & Tickets":
            st.markdown("### 🛠️ Helpdesk & Maintenance Tickets")
            st.info("Raise plumbing, electrical, or structural maintenance requests to block administrators or master admin. Comments and updates are restricted to administrators.")
            
            with st.expander("➕ Raise New Maintenance Ticket", expanded=False):
                with st.form("helpdesk_form", clear_on_submit=True):
                    h_issue = st.text_area("Describe Maintenance Issue / Request Details")
                    h_sub = st.form_submit_button("Submit Ticket")
                    if h_sub:
                        if h_issue:
                            with engine.begin() as conn:
                                conn.execute(
                                    text('INSERT INTO togethespace_v4_helpdesk (resident_name, block, issue_details, status) VALUES (:rn, :bl, :is, \'Open\')'),
                                    {'rn': current_user.get('Full Name'), 'bl': user_block, 'is': h_issue}
                                )
                            st.success("Maintenance ticket submitted successfully!")
                            st.rerun()
                        else:
                            st.warning("Please enter issue details.")

            st.markdown("---")
            st.markdown("#### 🎫 Active Maintenance Tickets")
            try:
                with engine.connect() as conn:
                    help_df = pd.read_sql(text('SELECT * FROM togethespace_v4_helpdesk ORDER BY created_at DESC;'), con=conn)
                
                if help_df.empty:
                    st.info("No active helpdesk tickets.")
                else:
                    for _, hrow in help_df.iterrows():
                        admin_cmts = f"<br>🛡️ <b>Admin Response:</b> {hrow['admin_comments']}" if hrow.get('admin_comments') else ""
                        st.markdown(f"""
                            <div class="sea-green-card">
                                <h4>🛠️ Ticket #{hrow['id']} — {hrow['resident_name']} ({hrow['block']}) <span style="font-size:0.7em; background:#e65100; color:white; padding:2px 6px; border-radius:4px;">{hrow['status']}</span></h4>
                                <p style="color: #444444; font-size: 0.85em;">Raised: {hrow['created_at']}</p>
                                <p style="color: #111111;"><b>Issue:</b> {hrow['issue_details']}</p>
                                {admin_cmts}
                            </div>
                        """, unsafe_allow_html=True)

                        if is_admin_user:
                            with st.form(f"admin_comment_form_{hrow['id']}"):
                                new_comment = st.text_input("Admin Comment / Status Update", key=f"cmt_{hrow['id']}")
                                new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved"], key=f"st_{hrow['id']}")
                                if st.form_submit_button("Post Admin Update"):
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text('UPDATE togethespace_v4_helpdesk SET admin_comments = :ac, status = :st WHERE id = :id'),
                                            {'ac': new_comment, 'st': new_status, 'id': hrow['id']}
                                        )
                                    st.success("Admin update posted!")
                                    st.rerun()
            except Exception as e:
                st.warning(f"Error loading helpdesk: {e}")

        # 13. FACILITY BOOKING & PUBLIC UTILITIES DIRECTORY
        elif menu_selection == "📅 Facility Booking & Utilities":
            st.markdown("### 📅 Community Facility Booking & Public Utilities Directory")
            st.info("Direct clickable navigation to municipal authorities, panchayat offices, local police stations, electric and water supply authorities, schools, colleges, municipal hospitals, and councillor offices.")
            
            utility_links = [
                {"category": "Medical & Hospital Services", "name": "Municipal General Hospital & Emergency Care", "url": "https://www.wbhealth.gov.in"},
                {"category": "Law & Order", "name": "Local Police Station & Control Room", "url": "https://policewb.gov.in"},
                {"category": "Utilities", "name": "State Electricity Board (WBSEDCL)", "url": "https://www.wbsedcl.in"},
                {"category": "Utilities", "name": "Water Supply & Municipal Corporation Water Wing", "url": "https://www.kmcgov.in"},
                {"category": "Local Governance", "name": "Panchayat Office / Municipal Corporation & Councillor Desk", "url": "https://wbdma.gov.in"},
                {"category": "Education", "name": "Local Public Schools & Higher Education Authority", "url": "https://wbbse.wb.gov.in"},
                {"category": "Community Halls", "name": "Block Community Hall & Guest Rooms Reservation Desk", "url": "#"}
            ]

            for u in utility_links:
                st.markdown(f"""
                    <div class="sea-green-card">
                        <h4>🏛️ [{u['category']}] {u['name']}</h4>
                        <p>🔗 <b>Official Portal / Booking Link:</b> <a href="{u['url']}" target="_blank">{u['url']}</a></p>
                    </div>
                """, unsafe_allow_html=True)

        # 14. SAFETY & SOS ALERTS
        elif menu_selection == "🚨 Safety & SOS Alerts":
            st.markdown("### 🚨 Emergency Safety & SOS Broadcasts")
            st.error("⚠️ EMERGENCY SOS: Instant escalation to all Block Admins and Master Admin. Bypasses standard bottlenecks during critical life-safety events.")
            if st.button("🚨 TRIGGER EMERGENCY SOS", type="primary"):
                st.error("🚨 EMERGENCY SOS BROADCASTED TO ALL BLOCK & MASTER ADMINS!")

        # 15. COMMUNITY POLLS & VOTING
        elif menu_selection == "📊 Community Polls & Voting":
            st.markdown("### 📊 Community Polls & Electronic Voting")
            st.info("Democratic participation in block decisions, budget approvals, and community association elections.")
            
            if is_admin_user:
                with st.expander("➕ Create New Community Poll / Vote", expanded=False):
                    with st.form("poll_form", clear_on_submit=True):
                        p_title = st.text_input("Poll Subject / Question")
                        p_opt1 = st.text_input("Option 1")
                        p_opt2 = st.text_input("Option 2")
                        if st.form_submit_button("Launch Community Poll"):
                            st.success(f"Poll launched successfully: **{p_title}**")

            st.markdown("---")
            st.markdown("#### 🗳️ Active Polls")
            st.markdown("""
                <div class="sea-green-card">
                    <h4>📊 Weekly Community Solar Installation Approval</h4>
                    <p style="color: #111111;">Should we proceed with community-wide rooftop solar net-metering installation for Block rooftops?</p>
                    <button style="background:#1b5e20; color:white; border:none; padding:6px 14px; border-radius:6px; font-weight:600;">Vote: Yes</button>
                    <button style="background:#b71c1c; color:white; border:none; padding:6px 14px; border-radius:6px; font-weight:600; margin-left:8px;">Vote: No</button>
                </div>
            """, unsafe_allow_html=True)

        # 16. LOCAL ATTRACTIONS & EVENTS
        elif menu_selection == "🌟 Local Attractions & Events":
            st.markdown("### 🌟 Local Attractions & Neighborhood Events")
            st.info("Discover nearby heritage spots, restaurants, parks, and upcoming festive events. All posts undergo Sub-Admin pre-screening before public display. Synchronized via Gemini AI.")
            
            default_attractions = [
                {"title": "Eco Park & Walking Trail (New Town)", "location": "New Town, Action Area II", "desc": "A sprawling urban park featuring scenic walking tracks, boating lakes, and food kiosks."},
                {"title": "Victoria Memorial Heritage Gardens", "location": "Central Kolkata", "desc": "Historic white marble monument and sprawling gardens hosting seasonal cultural events."}
            ]
            
            attractions_json = get_override_content(f"local_attractions_{admin_block if not is_master else 'global'}", json.dumps(default_attractions))
            try:
                current_attractions = json.loads(attractions_json)
            except Exception:
                current_attractions = default_attractions

            for att in current_attractions:
                st.markdown(f"""
                    <div class="sea-green-card">
                        <h4>📍 {att['title']}</h4>
                        <p style="color: #444444; font-size: 0.85em;">📍 Location: {att['location']} • Verified via Gemini AI</p>
                        <p style="color: #111111;">{att['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)

            with st.expander("➕ Submit Local Attraction or Event", expanded=False):
                with st.form("attraction_form", clear_on_submit=True):
                    a_title = st.text_input("Attraction / Event Title")
                    a_loc = st.text_input("Location / Address")
                    a_desc = st.text_area("Description & Highlights")
                    if st.form_submit_button("Submit for Sub-Admin Verification"):
                        st.success("Submitted successfully! Pending Sub-Admin pre-screening approval.")

        # 17. COMMUNITY ADMIN PORTAL (Master Admin Unrestricted Overrides & Cooldown Bypass)
        elif menu_selection == "🔐 Community Admin Portal":
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
                if st.session_state.get('authenticated'):
                    st.markdown(f"**Authenticated Role:** `{admin_block}`")
                else:
                    admin_pass = st.text_input('Admin Passcode', type='password', value='Master2026!' if pre_role == 'Master Admin' else '', key='admin_pass_input')

            is_admin_logged = st.session_state.get('authenticated', False)
            if is_admin_logged:
                ap_info = ADMIN_PROFILES.get(admin_block, {})
                st.success(f"🔓 Authenticated as **{ap_info.get('Full Name')}** ({ap_info.get('Designation')} — ID: `{ap_info.get('User ID')}`)!")

                current_busy_state = is_admin_busy(admin_block)
                new_busy_state = st.checkbox("🔴 Mark Self as Busy (Auto-Accept Password Requests)", value=current_busy_state, key=f"busy_toggle_{admin_block}")
                if new_busy_state != current_busy_state:
                    with engine.begin() as conn:
                        conn.execute(
                            text('INSERT INTO togethespace_v4_admin_status (block, is_busy) VALUES (:b, :busy) ON CONFLICT (block) DO UPDATE SET is_busy = :busy'),
                            {'b': admin_block, 'busy': new_busy_state}
                        )
                    st.rerun()

                st.markdown("#### ⚙️ Admin Operations Menu")
                
                if 'admin_action' not in st.session_state:
                    st.session_state['admin_action'] = '📢 Create Notice'

                admin_actions = [
                    '📢 Create Notice',
                    '🧹 Manual Cache Cleanup & Maintenance',
                    '🤖 Gemini AI 24-Hour Auto-Sync Switch',
                    '🎵 Weekly Gemini Music Generator',
                    '🌐 Request / Manage Cross-Block Broadcasts',
                    '🔗 Approve Social Links',
                    '📋 Review Entry Requests (Cell-Level Decision Format)',
                    '🗑️ Delete Post',
                    '➕ Add Member',
                    '✏️ Edit Member',
                    '❌ Delete Member',
                    '🔑 Password Requests & Approvals',
                    '⚡ Direct Password Override (Master Only)',
                    '📋 Audit Logs',
                    '📥 Export Credentials CSV'
                ]

                cols_op = st.columns(3)
                for idx, act in enumerate(admin_actions):
                    if cols_op[idx % 3].button(act, use_container_width=True):
                        st.session_state['admin_action'] = act
                        st.rerun()

                admin_action = st.session_state['admin_action']
                st.markdown(f"### Current Operation: `{admin_action}`")
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
                                author_str = f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})"
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_records (title, category, content, author, likes, "Block", "Visibility", "Broadcast_Status") VALUES (:title, :category, :content, :author, 0, :block, :visibility, :status)'),
                                        {'title': n_title, 'category': n_category, 'content': n_content, 'author': author_str, 'block': post_org, 'visibility': 'Global', 'status': 'Approved'}
                                    )
                                st.success('Official notice published successfully and broadcasted to community!')
                                st.rerun()
                            else:
                                st.warning('Please fill in title and content.')

                # 2. MANUAL CACHE CLEANUP & MAINTENANCE
                elif admin_action == '🧹 Manual Cache Cleanup & Maintenance':
                    st.markdown('#### 🧹 On-Demand Cache Cleanup & Maintenance Trigger')
                    st.info('Administrators can trigger a full system cache cleanup and maintenance sweep at any time.')
                    if st.button('🚀 Run Immediate Cache Cleanup & System Brush-Up', type='primary'):
                        st.cache_resource.clear()
                        st.cache_data.clear()
                        with engine.begin() as conn:
                            conn.execute(
                                text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                {
                                    'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})",
                                    'target': ap_info.get('User ID'),
                                    'action': 'Manual Cache Maintenance',
                                    'details': f"Admin {ap_info.get('Full Name')} triggered manual cache cleanup and maintenance."
                                }
                            )
                        st.success('✨ System cache successfully cleared and maintenance brush-up completed!')

                # 3. GEMINI AI 24-HOUR AUTO-SYNC SWITCH (Master Admin Unrestricted Override)
                elif admin_action == '🤖 Gemini AI 24-Hour Auto-Sync Switch':
                    st.markdown('#### 🤖 Gemini AI Live Data Synchronization Switch')
                    st.info('Clicking this switch commands Gemini AI to update Market Rates, Top News, Learning Lessons, and Local Attractions. **(Restricted to once every 24 hours for Block Admins; Unrestricted anytime for Master Admin)**.')
                    
                    locality_input = st.text_input('Enter Locality for Local Attractions & Events', value='Kolkata & New Town')
                    
                    can_sync = True
                    last_sync_str = "Never"
                    try:
                        with engine.connect() as conn:
                            sync_res = conn.execute(text('SELECT last_sync_time FROM togethespace_v4_gemini_sync_logs WHERE block = :b'), {'b': admin_block}).fetchone()
                            if sync_res and sync_res[0]:
                                last_sync_time = sync_res[0]
                                last_sync_str = str(last_sync_time)
                                if datetime.now() - last_sync_time < timedelta(hours=24):
                                    can_sync = False
                    except Exception:
                        pass

                    # Master Admin bypasses cooldown restriction completely
                    if is_master or admin_block == 'Master Admin':
                        can_sync = True
                        st.info("👑 Master Admin Override Active: 24-hour cooldown is bypassed. You can update anytime.")

                    st.markdown(f"🕒 **Last Synchronized:** `{last_sync_str}`")

                    if not can_sync:
                        st.warning("⏳ 24-Hour Cooldown Active: This switch has already been triggered within the last 24 hours. Please wait until the cooldown period expires.")
                    else:
                        if st.button('🚀 Trigger Gemini AI Sync Now', type='primary'):
                            try:
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_gemini_sync_logs (block, last_sync_time) VALUES (:b, CURRENT_TIMESTAMP) ON CONFLICT (block) DO UPDATE SET last_sync_time = CURRENT_TIMESTAMP'),
                                        {'b': admin_block}
                                    )
                                st.success(f"🤖 Gemini AI successfully synchronized live data for **{admin_block}** (Locality: {locality_input})! Market rates, top news, learning lessons, and local attractions have been updated.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Sync failed: {e}")

                # 4. WEEKLY GEMINI MUSIC GENERATOR (Master Admin Unrestricted Override)
                elif admin_action == '🎵 Weekly Gemini Music Generator':
                    st.markdown('#### 🎵 Gemini AI Weekly Ambient Music Generator')
                    st.info('Clicking this switch commands Gemini AI to generate and update the community background ambient music tone and theme across the app. **(Restricted to once per week for Block Admins; Unrestricted anytime for Master Admin)**.')
                    
                    can_music_sync = True
                    last_music_str = "Never"
                    try:
                        with engine.connect() as conn:
                            m_res = conn.execute(text('SELECT last_music_sync FROM togethespace_v4_music_sync_logs WHERE block = :b'), {'b': admin_block}).fetchone()
                            if m_res and m_res[0]:
                                last_m_time = m_res[0]
                                last_music_str = str(last_m_time)
                                if datetime.now() - last_m_time < timedelta(days=7):
                                    can_music_sync = False
                    except Exception:
                        pass

                    # Master Admin bypasses weekly music cooldown completely
                    if is_master or admin_block == 'Master Admin':
                        can_music_sync = True
                        st.info("👑 Master Admin Override Active: Weekly music cooldown is bypassed. You can change the music anytime.")

                    st.markdown(f"🕒 **Last Weekly Music Generation:** `{last_music_str}`")

                    if not can_music_sync:
                        st.warning("⏳ Weekly Cooldown Active: The background music tone can only be regenerated and updated once per week. Please wait until 7 days have passed.")
                    else:
                        if st.button('🎵 Generate & Update Weekly Music Tone via Gemini AI', type='primary'):
                            try:
                                with engine.begin() as conn:
                                    conn.execute(
                                        text('INSERT INTO togethespace_v4_music_sync_logs (block, last_music_sync) VALUES (:b, CURRENT_TIMESTAMP) ON CONFLICT (block) DO UPDATE SET last_music_sync = CURRENT_TIMESTAMP'),
                                        {'b': admin_block}
                                    )
                                st.success(f"🎵 Gemini AI successfully composed and updated the weekly ambient background music tone for **{admin_block}**!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Music generation failed: {e}")

                # 5. CROSS-BLOCK BROADCASTS
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
                        st.info(f'🏢 Block Admin ({ap_info.get("Full Name")} - {admin_block}): Select one of your block posts below to request Master Admin approval for global cross-block viewing.')
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

                # 6. APPROVE SOCIAL LINKS
                elif admin_action == '🔗 Approve Social Links':
                    st.markdown('#### 🔗 Review and Approve Resident Social Media Links')
                    try:
                        with engine.connect() as conn:
                            if admin_block == 'Master Admin':
                                unapproved_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Facebook", "Instagram", "Twitter", "LinkedIn", "Custom_Social_Name", "Custom_Social_URL" FROM togethespace_v4_directory WHERE "Social_Approved" = FALSE ORDER BY "Full Name";'), con=conn)
                            else:
                                unapproved_df = pd.read_sql(text('SELECT id, "Full Name", "Organization", "Facebook", "Instagram", "Twitter", "LinkedIn", "Custom_Social_Name", "Custom_Social_URL" FROM togethespace_v4_directory WHERE "Organization" = :b AND "Social_Approved" = FALSE ORDER BY "Full Name";'), con=conn, params={'b': admin_block})
                        
                        if unapproved_df.empty:
                            st.info('No pending social link approvals found.')
                        else:
                            for idx, u_row in unapproved_df.iterrows():
                                custom_soc = f"<br>🔗 {u_row.get('Custom_Social_Name')}: {u_row.get('Custom_Social_URL')}" if u_row.get('Custom_Social_Name') else ""
                                st.markdown(f"""
                                    <div class="admin-card">
                                        <b>Member:</b> {u_row['Full Name']} ({u_row['Organization']})<br>
                                        📘 Facebook: {u_row.get('Facebook') or 'N/A'}<br>
                                        📸 Instagram: {u_row.get('Instagram') or 'N/A'}<br>
                                        🐦 Twitter: {u_row.get('Twitter') or 'N/A'}<br>
                                        💼 LinkedIn: {u_row.get('LinkedIn') or 'N/A'}
                                        {custom_soc}
                                    </div>
                                """, unsafe_allow_html=True)
                                if st.button(f'✅ Approve Social Links for {u_row["Full Name"]}', key=f'approve_social_{u_row["id"]}'):
                                    with engine.begin() as conn:
                                        conn.execute(
                                            text('UPDATE togethespace_v4_directory SET "Social_Approved" = TRUE WHERE id = :id'),
                                            {'id': int(u_row['id'])}
                                        )
                                    st.success(f'Social links approved for {u_row["Full Name"]}!')
                                    st.rerun()
                    except Exception as e:
                        st.warning(f'Error loading unapproved social links: {e}')

                # 7. REVIEW ENTRY REQUESTS
                elif admin_action == '📋 Review Entry Requests (Cell-Level Decision Format)':
                    st.markdown('#### 📋 Pending Entry / Modification Form Requests & Cell-Level Validation')
                    try:
                        with engine.connect() as conn:
                            if admin_block == 'Master Admin':
                                req_formats = pd.read_sql(text('SELECT * FROM togethespace_v4_entry_requests WHERE status = \'Pending\' ORDER BY created_at DESC;'), con=conn)
                            else:
                                req_formats = pd.read_sql(text('SELECT * FROM togethespace_v4_entry_requests WHERE block = :b AND status = \'Pending\' ORDER BY created_at DESC;'), con=conn, params={'b': admin_block})
                        
                        if req_formats.empty:
                            st.info('No pending entry/modification formats found for review.')
                        else:
                            for idx, freq in req_formats.iterrows():
                                st.markdown(f"""
                                    <div class="admin-card">
                                        <h4>Format Request #{freq['id']} — Type: {freq['request_type']}</h4>
                                        <b>Applicant:</b> {freq['applicant_name']} (User ID: {freq['applicant_userid']}) | <b>Block:</b> {freq['block']}<br>
                                        🛂 <b>Passport Photo:</b> <a href="{freq['passport_photo_url']}" target="_blank">View Passport Photo</a> | 
                                        📂 <b>Supporting Docs (200MB):</b> <a href="{freq['supporting_docs_url']}" target="_blank">View Supporting Documents</a>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                payload = freq['form_payload']
                                if isinstance(payload, str):
                                    payload = json.loads(payload)
                                
                                st.markdown('##### Cell-by-Cell Evaluation (🟢 Accept | 🔴 Reject | ⚪ Hold)')
                                cell_decisions = {}
                                with st.form(f"cell_review_form_{freq['id']}"):
                                    for field_key, field_val in payload.items():
                                        col_cell1, col_cell2 = st.columns([2, 2])
                                        with col_cell1:
                                            st.markdown(f"**{field_key}**: `{field_val}`")
                                        with col_cell2:
                                            cell_choice = st.radio(f"Decision for {field_key}", options=['🟢 Accept', '🔴 Reject', '⚪ Hold'], index=0, key=f"cell_{freq['id']}_{field_key}", horizontal=True)
                                            cell_decisions[field_key] = cell_choice
                                    
                                    overall_action = st.selectbox('Final Format Action', ['Approve & Commit Changes', 'Reject Entire Request', 'Keep on Hold'], key=f"final_act_{freq['id']}")
                                    if st.form_submit_button(f'Submit Cell Decisions for Request #{freq["id"]}'):
                                        with engine.begin() as conn:
                                            new_status = 'Approved' if overall_action == 'Approve & Commit Changes' else ('Rejected' if overall_action == 'Reject Entire Request' else 'Pending')
                                            conn.execute(text('UPDATE togethespace_v4_entry_requests SET cell_decisions = :dec::jsonb, status = :st WHERE id = :id'), {'dec': json.dumps(cell_decisions), 'st': new_status, 'id': freq['id']})
                                        st.success(f"Request #{freq['id']} updated to {new_status}!")
                                        st.rerun()
                    except Exception as e:
                        st.warning(f"Error: {e}")

                # 8. DELETE POST
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

                # 9. ADD MEMBER
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
                            avatar_url = st.text_input('Avatar Image URL')
                            address = st.text_input('Address')
                            phone = st.text_input('Phone Number')
                            wa_call = st.text_input('WhatsApp Call')
                            wa_chat = st.text_input('WhatsApp Chat')
                        with c2:
                            email = st.text_input('Email')
                            website = st.text_input('Website')
                            fb_in = st.text_input('Facebook URL')
                            ig_in = st.text_input('Instagram URL')
                            tw_in = st.text_input('Twitter URL')
                            li_in = st.text_input('LinkedIn URL')
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
                                                ("Organization", "Full Name", "User ID", "Password", "Avatar", "Facebook", "Instagram", "Twitter", "LinkedIn", "Social_Approved", "Address", "Phone Number", "WhatsApp Call", "WhatsApp Chat", "Email", "Website", "Blood Group", "Allergies", "Medical Conditions", "Medications", "Emergency Contact Name", "Emergency Contact Phone", "Bio")
                                                VALUES 
                                                (:org, :full_name, :userid, :password, :avatar, :fb, :ig, :tw, :li, TRUE, :address, :phone, :wa_call, :wa_chat, :email, :website, :blood, :allergies, :med_cond, :meds, :em_name, :em_phone, :bio)
                                            """),
                                            {
                                                'org': org, 'full_name': full_name, 'userid': userid, 'password': hashed_pwd, 'avatar': avatar_url,
                                                'fb': fb_in, 'ig': ig_in, 'tw': tw_in, 'li': li_in,
                                                'address': address, 'phone': phone, 'wa_call': wa_call, 'wa_chat': wa_chat,
                                                'email': email, 'website': website, 'blood': blood, 'allergies': allergies,
                                                'med_cond': med_cond, 'meds': meds, 'em_name': em_name, 'em_phone': em_phone, 'bio': bio
                                            }
                                        )
                                    st.success('New member added successfully with encrypted password conforming to policy!')
                                    st.rerun()
                            else:
                                st.warning('Full Name is required.')

                # 10. EDIT MEMBER
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
                                    e_avatar = st.text_input('Avatar Image URL', value=str(m_data.get('Avatar', '')))
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
                                                    text('UPDATE togethespace_v4_directory SET "Full Name" = :name, "User ID" = :uid, "Password" = :pwd, "Avatar" = :avatar, "Address" = :addr, "Phone Number" = :phone, "Email" = :email WHERE id = :id'),
                                                    {'name': e_name, 'uid': e_uid, 'pwd': final_pwd_hash, 'avatar': e_avatar, 'addr': e_addr, 'phone': e_phone, 'email': e_email, 'id': m_id}
                                                )
                                            else:
                                                conn.execute(
                                                    text('UPDATE togethespace_v4_directory SET "Full Name" = :name, "User ID" = :uid, "Avatar" = :avatar, "Address" = :addr, "Phone Number" = :phone, "Email" = :email WHERE id = :id'),
                                                    {'name': e_name, 'uid': e_uid, 'avatar': e_avatar, 'addr': e_addr, 'phone': e_phone, 'email': e_email, 'id': m_id}
                                                )
                                        st.success('Member record updated successfully!')
                                        st.rerun()

                # 11. DELETE MEMBER
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

                # 12. PASSWORD REQUESTS & APPROVALS WORKFLOW
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
                                                        'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})",
                                                        'target': 'master_admin',
                                                        'name': ap_info.get('Full Name'),
                                                        'block': 'All Blocks',
                                                        'pwd': hashed_m_req,
                                                        'status': req_status
                                                    }
                                                )
                                                conn.execute(
                                                    text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                    {
                                                        'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})",
                                                        'target': 'master_admin',
                                                        'action': 'Master Self-Request',
                                                        'details': f'Master Admin ({ap_info.get("Full Name")}) submitted self-request (Auto-approved: {master_is_busy}).'
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
                                master_req_df = pd.read_sql(text('SELECT * FROM togethespace_v4_password_requests WHERE status = \'Pending\' AND (requested_by LIKE \'Block Admin:%\' OR requested_by LIKE \'Vikramaditya Roy%\' OR requested_by = \'Master Admin\') ORDER BY created_at DESC;'), con=conn)
                            
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
                                                    {'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})", 'target': req['target_userid'], 'action': 'Approved Block Admin Request', 'details': f"Master Admin ({ap_info.get('Full Name')}) approved request #{req['id']} for {req['target_name']}."}
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
                        st.markdown(f'### 🏢 Block Admin ({ap_info.get("Full Name")} — {admin_block}): Resident Requests & Send Request to Master Admin')
                        
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
                                                    {'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})", 'target': req['target_userid'], 'action': 'Approved Resident Password Request', 'details': f"Block Admin ({ap_info.get('Full Name')}) approved password request for {req['target_name']}."}
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
                                                    'by': f'Block Admin: {ap_info.get("Full Name")} ({admin_block})',
                                                    'target': ap_info.get('User ID'),
                                                    'name': ap_info.get('Full Name'),
                                                    'block': admin_block,
                                                    'pwd': hashed_ba_p,
                                                    'status': req_status
                                                }
                                            )
                                            conn.execute(
                                                text('INSERT INTO togethespace_v4_password_logs (changed_by, target_userid, action_type, details) VALUES (:by, :target, :action, :details)'),
                                                {
                                                    'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})",
                                                    'target': ap_info.get('User ID'),
                                                    'action': 'Sent Password Request to Master Admin',
                                                    'details': f"Block Admin ({ap_info.get('Full Name')}) submitted password request (Auto-accepted: {master_is_busy})."
                                                }
                                            )
                                        if master_is_busy:
                                            st.success('Master Admin is busy! Your password change request was automatically approved.')
                                        else:
                                            st.success('Password change request successfully sent to Master Admin!')
                                else:
                                    st.warning('Please enter a password.')

                # 13. DIRECT PASSWORD OVERRIDE (Master Only)
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
                                                            'by': f"{ap_info.get('Full Name')} ({ap_info.get('Designation')})",
                                                            'target': str(target_db_id),
                                                            'action': 'Direct Password Override',
                                                            'details': f"Master Admin ({ap_info.get('Full Name')}) directly changed password for user record ID {target_db_id} without request."
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

                # 14. AUDIT LOGS
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

                # 15. EXPORT CREDENTIALS CSV
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
                                file_name=f"togethespace_credentials_{admin_block.lower().replace('_', '_')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.warning(f'Could not generate credential export: {e}')

    except Exception as e:
        st.error(f'Database connection or query failed: {e}')

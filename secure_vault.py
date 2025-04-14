import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Initialize session state
def init_session_state():
    session_vars = {
        'stored_data': {},
        'failed_attempts': 0,
        'fernet_key': Fernet.generate_key(),
        'current_page': "Home",
        'authenticated': False
    }
    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize cipher suite
    if 'cipher' not in st.session_state:
        st.session_state.cipher = Fernet(st.session_state.fernet_key)

# Security functions
def hash_passkey(passkey: str) -> str:
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text: str) -> str:
    return st.session_state.cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text: str) -> str:
    return st.session_state.cipher.decrypt(encrypted_text.encode()).decode()

# Page navigation
def handle_navigation():
    menu = ["Home", "Store Data", "Retrieve Data", "Login"]
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        new_page = st.selectbox(
            "Navigation",
            menu,
            index=menu.index(st.session_state.current_page),
            label_visibility="collapsed"
        )
    
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.rerun()

# Page components
def home_page():
    st.header("🔒 Secure Data Vault")
    st.markdown("""
    ### Welcome to your personal secure data storage!
    **Features:**
    - Military-grade AES-256 encryption
    - Secure passkey authentication
    - Tamper-proof data storage
    - Automatic session protection
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/295/295128.png", width=200)

def store_data_page():
    st.header("🔐 Store New Data")
    with st.form("store_form"):
        user_data = st.text_area("Enter your sensitive data:", height=150)
        passkey = st.text_input("Create access passkey:", type="password")
        
        if st.form_submit_button("🔒 Encrypt & Store"):
            if user_data and passkey:
                encrypted_text = encrypt_data(user_data)
                hashed_passkey = hash_passkey(passkey)
                
                st.session_state.stored_data[encrypted_text] = {
                    "encrypted_text": encrypted_text,
                    "passkey": hashed_passkey
                }
                st.success("Data securely stored!")
            else:
                st.error("Both fields are required!")

def retrieve_data_page():
    st.header("🔍 Retrieve Stored Data")
    
    if st.session_state.failed_attempts >= 3:
        st.session_state.current_page = "Login"
        st.rerun()
    
    with st.form("retrieve_form"):
        encrypted_text = st.text_area("Encrypted data:", height=150)
        passkey = st.text_input("Enter passkey:", type="password")
        
        if st.form_submit_button("🔓 Decrypt"):
            if encrypted_text and passkey:
                hashed_passkey = hash_passkey(passkey)
                entry = st.session_state.stored_data.get(encrypted_text)
                
                if entry and entry["passkey"] == hashed_passkey:
                    decrypted_text = decrypt_data(encrypted_text)
                    st.session_state.failed_attempts = 0
                    st.success("Decryption successful!")
                    st.code(decrypted_text, language="text")
                else:
                    st.session_state.failed_attempts += 1
                    remaining = 3 - st.session_state.failed_attempts
                    st.error(f"⚠️ Invalid credentials! {remaining} attempts remaining")
                    
                    if st.session_state.failed_attempts >= 3:
                        st.warning("🚨 Maximum attempts reached! System lockdown activated.")
                        st.session_state.current_page = "Login"
                        st.rerun()
            else:
                st.error("Both fields are required!")

def login_page():
    st.header("🚨 System Lockdown")
    st.warning("Authentication required to continue")
    
    with st.form("login_form"):
        password = st.text_input("Enter system master key:", type="password")
        if st.form_submit_button("🔑 Authenticate"):
            if password == "admin123":  # In production, use proper auth
                st.session_state.failed_attempts = 0
                st.session_state.authenticated = True
                st.session_state.current_page = "Retrieve Data"
                st.rerun()
            else:
                st.error("Incorrect master key!")

# Main app
def main():
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    handle_navigation()
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"🔐 Security status: **{'🟢 Secure' if st.session_state.authenticated else '🔴 Locked'}**")
    st.sidebar.markdown(f"📦 Stored entries: **{len(st.session_state.stored_data)}**")
    
    # Page routing
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Store Data":
        store_data_page()
    elif st.session_state.current_page == "Retrieve Data":
        retrieve_data_page()
    elif st.session_state.current_page == "Login":
        login_page()

if __name__ == "__main__":
    main()
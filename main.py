import streamlit as st
import pandas as pd
import os
from admin import display_admin_panel  # Import the admin panel function
from m_profile import display_profile  # Import the profile display function
from file_process import upload_receipt  # Import the upload function

# Set page configuration
st.set_page_config(page_title="Projek 10", page_icon="🔐", layout="centered")

# Load user credentials from a CSV file
def load_user_credentials():
    credentials_file = 'user_credentials.csv'
    if os.path.exists(credentials_file):
        df = pd.read_csv(credentials_file)
        return {row['username']: row['password'] for index, row in df.iterrows()}
    return {}

# Function to check login credentials
def login(username, password, user_credentials):
    return username in user_credentials and user_credentials[username] == password

# Function to display the login page
def display_login(user_credentials):
    st.title("Login Page")
    st.write("Please login to continue.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        # Check if user is the admin
        if username == "admin" and password == "admin_password":  # Change to a more secure method if necessary
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['is_admin'] = True
            st.success(f"Welcome, {username.title()}!")
            st.session_state['redirect_to_profile'] = False  # Reset redirection flag
            st.rerun()  # Rerun to refresh the session state
        elif login(username, password, user_credentials):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['is_admin'] = False
            st.success(f"Welcome, {username}!")
            st.session_state['redirect_to_profile'] = True  # Set redirection flag
            st.rerun()  # Rerun to refresh the session state
        else:
            st.error("Incorrect username or password")

# Function to display the logged-in user's dashboard inside the sidebar
def display_dashboard_sidebar():
    with st.sidebar:
        st.title(f"Welcome, {st.session_state['username']}")
        st.write("You are successfully logged in.")

        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('admin_access', None)  # Clear admin access state
            st.session_state.pop('admin_authenticated', None)  # Clear admin auth state
            st.session_state.pop('redirect_to_profile', None)  # Clear redirection flag
            st.rerun()  # Rerun to refresh the session state

        # Link to access admin panel
        if st.session_state['is_admin']:
            if st.button("Admin Access"):
                st.session_state['admin_access'] = True
                st.rerun()  # Rerun to show the admin panel

# Main logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'admin_access' not in st.session_state:
    st.session_state['admin_access'] = False

if 'admin_authenticated' not in st.session_state:
    st.session_state['admin_authenticated'] = False

if 'redirect_to_profile' not in st.session_state:
    st.session_state['redirect_to_profile'] = False

# Load user credentials from CSV
user_credentials = load_user_credentials()

if not st.session_state['logged_in']:
    display_login(user_credentials)
else:
    display_dashboard_sidebar()

    if st.session_state['redirect_to_profile']:
        selected_profile = display_profile()  # Call the profile display function and capture the selected profile

        # Show the receipt upload interface after profile selection
        username = st.session_state['username']  # Get the logged-in username
        st.subheader("Upload Receipt")
        upload_receipt(username, selected_profile)  # Call the upload function with the selected profile

    elif st.session_state['admin_access']:
        display_admin_panel()

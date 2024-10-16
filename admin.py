import streamlit as st
import pandas as pd
import os

# Admin credentials (should be kept secure)
admin_username = "admin"
admin_password = "admin_password"  # Change this to a more secure password

# Base directory to store user folders
BASE_DIR = 'user_folders'

# Function to save user credentials to CSV file
def save_credentials_to_csv(username, password):
    # Validate the username
    if not username.islower() or " " in username:
        return False  # Invalid username

    # Load existing credentials
    credentials_file = 'user_credentials.csv'
    if os.path.exists(credentials_file):
        df = pd.read_csv(credentials_file)

        # Check if the username already exists
        if username in df['username'].values:
            return False  # Username already exists
    else:
        df = pd.DataFrame(columns=['username', 'password'])

    # Create a new DataFrame for the new user
    new_user_df = pd.DataFrame({'username': [username], 'password': [password]})

    # Concatenate the existing DataFrame with the new user DataFrame
    df = pd.concat([df, new_user_df], ignore_index=True)

    # Save to CSV
    df.to_csv(credentials_file, index=False)

    # Create a new folder for the user
    user_folder = os.path.join(BASE_DIR, username)
    os.makedirs(user_folder, exist_ok=True)
    st.rerun()

    return True  # User added successfully

# Function to load user credentials from CSV
def load_credentials_from_csv():
    credentials_file = 'user_credentials.csv'
    if os.path.exists(credentials_file):
        return pd.read_csv(credentials_file)
    return pd.DataFrame(columns=['username', 'password'])

# Function to delete user credentials and their folder
def delete_user_credentials(username):
    # Load existing credentials
    df = load_credentials_from_csv()
    df = df[df['username'] != username]  # Keep only users that do not match the username
    df.to_csv('user_credentials.csv', index=False)  # Save the updated DataFrame

    # Delete the user's folder
    user_folder = os.path.join(BASE_DIR, username)
    if os.path.exists(user_folder):
        os.rmdir(user_folder)  # Remove the directory (make sure it's empty)

# Function to display the admin panel
def display_admin_panel():
    st.title("Admin Panel")

    # Admin password input
    if 'admin_authenticated' not in st.session_state:
        st.session_state['admin_authenticated'] = False

    if not st.session_state['admin_authenticated']:
        admin_pass = st.text_input("Enter Admin Password", type="password")
        authenticate_button = st.button("Authenticate")

        if authenticate_button:
            if admin_pass == admin_password:
                st.session_state['admin_authenticated'] = True
                st.success("Admin authenticated!")
                st.rerun()  # Rerun to refresh the session
            else:
                st.error("Incorrect password.")
    else:
        st.write("Add New User")

        # Initialize session state variables for new username and password
        if 'new_username' not in st.session_state:
            st.session_state['new_username'] = ''
        if 'new_password' not in st.session_state:
            st.session_state['new_password'] = ''

        with st.form("admin_form"):
            st.session_state['new_username'] = st.text_input("New Username", st.session_state['new_username'])
            st.session_state['new_password'] = st.text_input("New Password", type="password", value=st.session_state['new_password'])
            add_user_button = st.form_submit_button("Add User")

        if add_user_button:
            new_username = st.session_state['new_username']
            new_password = st.session_state['new_password']

            if new_username and new_password:
                # Save the new user credentials to CSV
                if save_credentials_to_csv(new_username, new_password):
                    # Clear the input fields by resetting session state variables

                    st.success(f"User '{new_username}' added successfully!")
                else:
                    st.error(f"Username '{new_username}' is invalid or already exists. Please choose a different username (lowercase and no spaces).")
            else:
                st.error("Please provide both username and password.")

        # Load and display existing users
        st.write("Existing Users:")
        df = load_credentials_from_csv()

        if not df.empty:
            for index, row in df.iterrows():
                col1, col2 = st.columns([1, 1])  # Create two columns for layout
                with col1:
                    st.write(row['username'])  # Display username
                with col2:
                    if st.button("Delete", key=row['username']):  # Create a delete button for each user
                        delete_user_credentials(row['username'])
                        st.success(f"User '{row['username']}' deleted successfully!")
                        st.rerun()  # Rerun to refresh the session
        else:
            st.write("No users found.")

# Run the admin panel function
if __name__ == "__main__":
    # Ensure the base directory exists
    os.makedirs(BASE_DIR, exist_ok=True)
    display_admin_panel()

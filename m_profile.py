import streamlit as st
import pandas as pd
import os

# Function to save profiles to CSV using DataFrame
def save_profiles_to_csv(profiles, username):
    df = pd.DataFrame(profiles, columns=["Profile"])
    os.makedirs(f'user_folders/{username}', exist_ok=True)  # Create directory if it doesn't exist
    df.to_csv(f'user_folders/{username}/profiles.csv', index=False)

# Function to load profiles from CSV
def load_profiles_from_csv(username):
    filename = f'user_folders/{username}/profiles.csv'
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df['Profile'].tolist()  # Return profiles as a list
    return []

# Function to delete a profile
def delete_profile(profile_name, profiles, username):
    profiles.remove(profile_name)
    save_profiles_to_csv(profiles, username)  # Save the updated profiles to CSV
    st.rerun()  # Reload the page after deletion

def download_profile(profile_name, username):
    # Define the file path for the profile's Excel file
    excel_file_path = f'user_folders/{username}/{profile_name}.xlsx'
    return excel_file_path

# Function to create a new Excel file for the profile
def create_excel_file(profile_name, username):
    # Create a new DataFrame for the profile
    df = pd.DataFrame(columns=["", "", ""])  # Customize the columns as needed
    excel_file_path = f'user_folders/{username}/{profile_name}.xlsx'
    df.to_excel(excel_file_path, index=False)  # Save the DataFrame to an Excel file

def display_profile():
    username = st.session_state['username']  # Get the logged-in username
    st.title("Automatic Receipt Recorder")
    st.write(f"Welcome to your profile page, {username}!")

    # Load existing profiles
    profiles = load_profiles_from_csv(username)

    # Ensure profiles is always a list (even if empty)
    if profiles is None:
        profiles = []  # If profiles are None, initialize as empty list

    # Add "None" and "Create New Profile" options to the profiles list
    profile_options = ["None"] + profiles + ["Create New Profile"]

    # Initialize session state for last selected profile
    if 'last_selected_profile' not in st.session_state:
        st.session_state['last_selected_profile'] = None

    # Dropdown to select profile
    selected_profile = st.selectbox("Select Profile", profile_options)

    # Check if the selected profile has changed
    if selected_profile != st.session_state['last_selected_profile']:
        # Clear uploader history if a different profile is selected
        st.session_state['uploader_history'] = []  # Clear uploader history
        st.session_state['last_selected_profile'] = selected_profile  # Update last selected profile

        # Refresh the session to reflect the changes
        st.session_state['refresh'] = True  # Set a flag to indicate refresh is needed
        st.rerun()  # Reload page to update dropdown

    # If "Create New Profile" is selected, show the input field to create a new profile
    if selected_profile == "Create New Profile":
        new_profile_name = st.text_input("Enter Profile Name:")
        if st.button("Create New Profile"):
            if new_profile_name:
                # Check if the profile name already exists
                if new_profile_name in profiles:
                    st.error("Profile name already exists. Please choose a different name.")
                else:
                    # Save new profile
                    profiles.append(new_profile_name)  # Append new profile to list
                    save_profiles_to_csv(profiles, username)  # Save to CSV
                    create_excel_file(new_profile_name, username)  # Create an Excel file for the new profile
                    st.success(f"Profile '{new_profile_name}' created successfully!")
                    st.session_state['last_selected_profile'] = new_profile_name  # Update last selected profile
                    st.rerun()  # Reload page to update dropdown
            else:
                st.error("Profile name cannot be empty.")
    else:
        # Display selected profile message
        if selected_profile != "None" and selected_profile != "Create New Profile":
            st.write(f"Profile '{selected_profile}' selected.")
            # Initialize confirm_deletion state if not present
            if 'confirm_deletion' not in st.session_state:
                st.session_state['confirm_deletion'] = False

            # Create two columns for Delete and Download buttons
            col1, col2 = st.columns(2)

            # Show the delete button in the first column
            with col1:
                if st.button("Delete Profile"):
                    st.session_state['confirm_deletion'] = True  # Show confirmation buttons

                # If deletion is confirmed, show confirm and cancel buttons
                if st.session_state['confirm_deletion']:
                    if st.button("Confirm Deletion", key="confirm_deletion_button"):
                        delete_profile(selected_profile, profiles, username)  # Call delete function
                        st.success(f"Profile '{selected_profile}' deleted successfully!")  # Show success message
                        st.session_state['confirm_deletion'] = False  # Reset the confirmation state
                        st.rerun()  # Reload to update profiles

                    if st.button("Cancel Deletion", key="cancel_deletion_button"):
                        st.session_state['confirm_deletion'] = False  # Hide confirmation buttons
                        st.rerun()  # Reload to update profiles

            # Show the download button in the second column
            with col2:
                if st.button("Download Profile"):
                    excel_file_path = download_profile(selected_profile, username)  # Get the Excel file path for download
                    if os.path.exists(excel_file_path):
                        with open(excel_file_path, "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=f"{selected_profile}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.error("The profile file does not exist.")

    # Display existing profiles in the sidebar
    st.sidebar.subheader("Profiles")
    if profiles:
        for profile in profiles:
            st.sidebar.text(profile)

    # Return the selected profile name
    return selected_profile  # Ensure to return this value


# To run the profile display function
if __name__ == "__main__":
    # Set a default username for demonstration, replace this with actual login logic in a real app
    if 'username' not in st.session_state:
        st.session_state['username'] = "test_user"

    display_profile()

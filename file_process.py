import openai
import streamlit as st
from PIL import Image
import pytesseract
import tiktoken
import pandas as pd
import os

# Access the API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Function to get response from GPT based on the extracted text
def get_gpt_response(extracted_text):
    """Get a response from GPT based on the extracted text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust the model if needed
            messages=[
                {"role": "user", "content": "Extract Store name:, Item Purchase:  and its corresponding Price. Ensure each item is on a new line without extra punctuation or symbols."},
                {"role": "user", "content": extracted_text},
            ],
        )
        return response['choices'][0]['message']['content'].strip()  # Extract and strip the GPT response
    except Exception as e:
        return f"Error fetching GPT response: {e}"

# Function to calculate the token count accurately
def calculate_token_count(messages):
    enc = tiktoken.encoding_for_model("gpt-4o-mini")  # Use the appropriate model
    token_count = 0
    for message in messages:
        token_count += len(enc.encode(message['content']))  # Accurate token count
    return token_count

# Function to update receipt details into an existing Excel file
def update_receipt_in_excel(gpt_response, profile_name, username):
    """Update the existing Excel file with the extracted receipt details."""
    lines = gpt_response.strip().split("\n")  # Split the response into lines
    store_name = lines[0].replace("Store name:", "").strip()  # Extract store name
    items = []

    # Loop through the remaining lines to extract items and prices
    for i in range(1, len(lines)):  # Start from the second line
        line = lines[i].strip()
        if line.startswith("Item Purchase:"):
            item_name = line.replace("Item Purchase:", "").strip()
            # The next line should contain the price
            if i + 1 < len(lines) and lines[i + 1].startswith("Price:"):
                price = lines[i + 1].replace("Price:", "").strip()
                items.append({"Store Name": store_name, "Item Purchased": item_name, "Price": price})
                i += 1  # Skip the price line since we already processed it

    # Define the path to the existing Excel file
    excel_file_path = f'user_folders/{username}/{profile_name}.xlsx'

    # Load the existing Excel file or create a new DataFrame if it doesn't exist
    if os.path.exists(excel_file_path):
        # Read the existing Excel file
        df = pd.read_excel(excel_file_path, engine='openpyxl')
    else:
        # Create a new DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=["Store Name", "Date", "Item Purchased", "Price"])

    # Create a new DataFrame for the new items
    new_items_df = pd.DataFrame(items)

    # Append new items to the DataFrame
    df = pd.concat([df, new_items_df], ignore_index=True)

    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file_path, index=False, engine='openpyxl')

    return excel_file_path  # Return the path of the updated Excel file

# Function to create a new Excel file for the profile
def create_excel_file(profile_name, username):
    # Create a new DataFrame for the profile
    df = pd.DataFrame(columns=["Store Name", "Date", "Item Purchased", "Price"])  # Customize the columns as needed
    excel_file_path = f'user_folders/{username}/{profile_name}.xlsx'
    df.to_excel(excel_file_path, index=False)  # Save the DataFrame to an Excel file

# Main function to handle receipt upload and display
def upload_receipt(username, selected_profile):
    # Hide upload tools if the selected profile is "None" or "Create New Profile"
    if selected_profile in ["None", "Create New Profile"]:
        st.warning("Please select a valid profile to upload receipts.")
        return  # Exit the function early if no valid profile is selected

    uploaded_file = st.file_uploader("Upload your receipt image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.success(f"Receipt '{uploaded_file.name}' uploaded successfully!")

        # Open the uploaded image
        image = Image.open(uploaded_file)

        # Resize the image (you can adjust the size as needed)
        max_size = (900, 900)  # Set maximum width and height to reduce data size
        image.thumbnail(max_size)
                # Convert the image to black and white (grayscale)
        bw_image = image.convert("L")

        # You can now perform OCR on bw_image

        # Optionally, display the black and white image
        #st.image(bw_image, caption="Black and White Receipt", use_column_width=True)

        # Use st.columns to create a two-column layout
        col1, col2 = st.columns([2, 2])  # Adjust width ratio as needed

        # Display the image in the first column
        with col1:
            st.image(image, caption='Uploaded Image', width=250)  # Width can be adjusted

        # Use OCR to extract text from the image
        extracted_text = pytesseract.image_to_string(image)

        # Prepare messages for token count
        messages = [
            {"role": "user", "content": "Answer any questions in the following text."},
            {"role": "user", "content": extracted_text}
        ]

        # Get GPT response based on the extracted text
        gpt_response = get_gpt_response(extracted_text)

        # Display the GPT response in the second column
        with col2:
            st.subheader("Receipt Details")
            st.write(gpt_response)

        # Calculate token count
        total_tokens = calculate_token_count(messages)

        # Display token count below the GPT response
        st.write(f"Total tokens for this request: {total_tokens}")

        # Call the update function after getting the GPT response
        # Call the update function after getting the GPT response
        if gpt_response:  # Ensure there's a response before saving
            excel_file_path = update_receipt_in_excel(gpt_response, selected_profile, username)
            st.success(f"Record Updated")
        
            # Read the updated Excel file
            df_updated = pd.read_excel(excel_file_path, engine='openpyxl')
        
            # Option 1: Sort the DataFrame by the index in reverse order (latest entry at the top)
            df_updated = df_updated.iloc[::-1].reset_index(drop=True)
        
            # Option 2: If using a 'Date' column, sort by 'Date' (uncomment this if you want to use this method)
            # df_updated = df_updated.sort_values(by='Date', ascending=False).reset_index(drop=True)
        
            # Display the updated records with the latest one at the top
            st.dataframe(df_updated)

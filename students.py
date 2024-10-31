import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_student_dashboard():
    st.title("Student Dashboard")
    
    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    
    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load both Content and Class worksheets from Google Sheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    content_worksheet = sheet.worksheet("Content")
    class_worksheet = sheet.worksheet("Class")

    # Fetch data
    content_data = content_worksheet.get_all_records()
    class_data = class_worksheet.get_all_records()

    # Convert to DataFrames
    content_df = pd.DataFrame(content_data)
    class_df = pd.DataFrame(class_data)

    # Display total number of classes
    num_classes = class_df.shape[0]
    st.write(f"Total Classes: {num_classes}")

    # Display each class as a collapsible section with related content
    for _, class_row in class_df.iterrows():
        class_name = class_row['Class Name']
        class_id = class_row['Class ID']
        
        with st.expander(f"{class_name} (ID: {class_id})"):
            # Filter content data for this specific class
            class_content = content_df[content_df['Week'] == class_name]  # Adjust if needed based on your data structure
            
            if not class_content.empty:
                for _, row in class_content.iterrows():
                    # Display type label for each content piece
                    if row['Type'] == "Material":
                        st.markdown("#### 📘 Material")
                    elif row['Type'] == "Assignment":
                        st.markdown("#### 📝 Assignment")
                    elif row['Type'] == "Question":
                        st.markdown("#### ❓ Question")
                    
                    # Display content details
                    st.write(f"**{row['Title']}**")
                    st.write(row['Content'])
                    if row['Link']:
                        st.write(f"[View Resource]({row['Link']})")
                    st.write("---")  # Separator between entries
            else:
                st.write("No content available for this class.")

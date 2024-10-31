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

    # Display each class as a collapsible section with related weekly content
    for _, class_row in class_df.iterrows():
        class_name = class_row['Class Name']
        
        with st.expander(f"{class_name}"):
            # Loop through each week and display all types of content for that week
            for week in sorted(content_df['Week'].unique()):
                st.subheader(f"Week {week}")

                # Filter content data for this specific week
                week_content = content_df[content_df['Week'] == week]
                
                if not week_content.empty:
                    for _, row in week_content.iterrows():
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
                    st.write("No content available for this week.")
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

    # Load both ContentID and Class worksheets from Google Sheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    content_worksheet = sheet.worksheet("ContentID")
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
        
        # Custom HTML styling for larger, bold class name
        class_title = f"<h3 style='font-weight: bold;'>{class_name}</h3>"
        
        with st.expander(st.markdown(class_title, unsafe_allow_html=True)):
            # Loop through each week and display content for that week
            for week in sorted(content_df['Week'].unique()):
                st.subheader(f"Week {week}")

                # Filter content data for this specific week
                week_content = content_df[content_df['Week'] == week]
                
                if not week_content.empty:
                    for _, row in week_content.iterrows():
                        # Emoji based on content type
                        if row['Type'] == "Material":
                            emoji = "📘"
                        elif row['Type'] == "Assignment":
                            emoji = "📝"
                        elif row['Type'] == "Question":
                            emoji = "❓"
                        else:
                            emoji = ""
                        
                        # Display only ID, emoji, and title for each content item
                        st.write(f"{row['ID']}: {emoji} **{row['Title']}**")
                else:
                    st.write("No content available for this week.")

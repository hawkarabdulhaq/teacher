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

    # Load Content, Class, and Week worksheets from Google Sheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    content_worksheet = sheet.worksheet("Content")
    class_worksheet = sheet.worksheet("Class")
    week_worksheet = sheet.worksheet("Week")

    # Fetch data from sheets
    content_data = content_worksheet.get_all_records()
    class_data = class_worksheet.get_all_records()
    week_data = week_worksheet.get_all_records()

    # Convert to DataFrames
    content_df = pd.DataFrame(content_data)
    class_df = pd.DataFrame(class_data)
    week_df = pd.DataFrame(week_data)

    # Map each class name to its weekly dates
    week_dates_map = {}
    for _, row in week_df.iterrows():
        class_name = row['Class Name']
        week_dates_map[class_name] = {
            "Week 1": row['Week 1'],
            "Week 2": row['Week 2'],
            "Week 3": row['Week 3'],
            "Week 4": row['Week 4']
        }

    # Display total number of classes
    num_classes = class_df.shape[0]
    st.write(f"Total Classes: {num_classes}")

    # Display each class as a collapsible section with related weekly content
    for _, class_row in class_df.iterrows():
        class_name = class_row['Class Name']
        
        # Use simple Markdown for bold text in the expander label
        class_title = f"**{class_name}**"
        
        with st.expander(label=class_title):
            # Get weekly dates for the current class
            weekly_dates = week_dates_map.get(class_name, {})

            # Loop through each week and display content for that week
            for week in sorted(content_df['Week'].unique()):
                st.subheader(f"Week {week}")

                # Filter content data for this specific week
                week_content = content_df[content_df['Week'] == week]
                
                if not week_content.empty:
                    for idx, (_, row) in enumerate(week_content.iterrows(), start=1):  # Use idx as the automatic order
                        # Emoji based on content type
                        if row['Type'] == "Material":
                            emoji = "📘"
                        elif row['Type'] == "Assignment":
                            emoji = "📝"
                        elif row['Type'] == "Question":
                            emoji = "❓"
                        else:
                            emoji = ""
                        
                        # Fetch the date for the current week for this class
                        date_for_week = weekly_dates.get(f"Week {week}", "Date not set")
                        
                        # Display automatic order, date, emoji, and title for each content item
                        st.write(f"{idx}: [{date_for_week}] {emoji} **{row['Title']}**")
                else:
                    st.write("No content available for this week.")

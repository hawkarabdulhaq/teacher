import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

def show_enroll_page():
    st.title("Enroll Page")
    st.write("Set the enrollment start date for each class. This will automatically schedule Week 1, Week 2, etc., and update the Post tab with the current week's date for each class.")

    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    
    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Enroll, Week, and Post worksheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    enroll_worksheet = sheet.worksheet("Enroll")
    week_worksheet = sheet.worksheet("Week")
    post_worksheet = sheet.worksheet("Post")

    # Fetch data from Enroll, Week, and Post sheets
    enroll_data = enroll_worksheet.get_all_records()
    enroll_df = pd.DataFrame(enroll_data)
    week_data = week_worksheet.get_all_records()
    week_df = pd.DataFrame(week_data)
    post_data = post_worksheet.get_all_records()
    post_df = pd.DataFrame(post_data)

    # Calculate the current "week" based on today’s date
    today = datetime.today()

    # Determine the week number (1 through 4) based on today’s date
    week_columns = ["Week 1", "Week 2", "Week 3", "Week 4"]
    for i, week_name in enumerate(week_columns, start=1):
        week_start_date = pd.to_datetime(week_df[week_name], format="%Y.%m.%d", errors='coerce')
        if not week_start_date.isnull().all():
            if any((today >= date) & (today < date + timedelta(weeks=1)) for date in week_start_date):
                current_week = i
                break
    else:
        current_week = None  # If no matching week found

    # Update dates for the current week in the Post tab
    if current_week:
        # Map each class name in the Post sheet to the class names in the Week sheet
        class_columns = post_df.columns[6:]  # Start from column G to the right
        for class_name in class_columns:
            # Find the row for this class in the Week tab
            class_row = week_df[week_df['Class Name'] == class_name]
            if not class_row.empty:
                # Get the date for the current week for this class
                week_date = class_row.iloc[0][week_columns[current_week - 1]]
                
                # Find the column index in the Post sheet for the class
                col_index = post_worksheet.find(class_name).col

                # Update the date in the Post sheet for the current week
                post_worksheet.update_cell(2, col_index, week_date)  # Update row 2 (where dates are written)

        st.success(f"Dates for Week {current_week} have been updated in the Post tab.")
    else:
        st.warning("Unable to determine the current week based on today's date.")

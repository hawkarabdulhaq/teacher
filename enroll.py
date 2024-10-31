import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

def show_enroll_page():
    st.title("Enroll Page")
    st.write("Set or update the enrollment start date for each class.")

    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Enroll worksheet from Google Sheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    enroll_worksheet = sheet.worksheet("Enroll")

    # Fetch data from the Enroll tab
    enroll_data = enroll_worksheet.get_all_records()
    enroll_df = pd.DataFrame(enroll_data)

    # Loop through each class and allow setting of enrollment start date
    for idx, row in enroll_df.iterrows():
        class_name = row['Class Name']
        current_date = row['Date']

        # Collapsible section for each class
        with st.expander(f"Class: {class_name}"):
            st.write("Set the start date for this class.")
            
            # Date input widget
            start_date = st.date_input(
                "Select Start Date",
                value=date.today() if pd.isnull(current_date) else pd.to_datetime(current_date).date(),
                key=f"date_{idx}"
            )
            
            # Update date button
            if st.button("Set Start Date", key=f"set_date_{idx}"):
                # Update the date in the Google Sheet
                enroll_worksheet.update_cell(idx + 2, 3, start_date.strftime("%Y-%m-%d"))  # +2 to account for header row
                st.success(f"Start date for '{class_name}' updated to {start_date}.")


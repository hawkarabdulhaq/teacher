import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def show_enroll_page():
    st.title("Enroll Page")
    st.write("Set the enrollment start date for each class.")

    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    
    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Enroll worksheet
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    enroll_worksheet = sheet.worksheet("Enroll")

    # Fetch data from Enroll sheet
    enroll_data = enroll_worksheet.get_all_records()
    enroll_df = pd.DataFrame(enroll_data)

    # Collect changes for batch update
    changes = []

    # Display each class with its enrollment date
    for i, row in enroll_df.iterrows():
        class_name = row['Class Name']
        current_date = row['Date']
        
        # Handle empty date cells by setting a default date (e.g., today's date)
        if current_date:
            try:
                parsed_date = datetime.strptime(current_date, "%d.%m.%Y")
            except ValueError:
                parsed_date = datetime.today()
        else:
            parsed_date = datetime.today()

        # Show class name and current enrollment date
        st.write(f"### {class_name}")
        st.write(f"Current Enrollment Date: {current_date or 'Not set'}")

        # Date input for updating the enrollment date
        new_date = st.date_input(f"Set new enrollment date for {class_name}", 
                                 value=parsed_date, 
                                 key=f"date_{i}")

        # Store the new date in the format required for the Google Sheet
        formatted_date = new_date.strftime("%d.%m.%Y")
        
        # Only add to changes if the date has changed
        if formatted_date != current_date:
            changes.append({
                "row": i + 2,  # Adjust for header row in Google Sheets
                "Date": formatted_date
            })
    
    # Submit button to save all changes
    if st.button("Submit All Changes"):
        for change in changes:
            enroll_worksheet.update_cell(change["row"], 3, change["Date"])  # Update Date column
        st.success("Enrollment dates updated successfully!")

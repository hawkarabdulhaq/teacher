import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

def show_enroll_page():
    st.title("Enroll Page")
    st.write("Set the enrollment start date for each class. This will automatically schedule Week 1, Week 2, etc., for each student.")

    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    
    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Enroll and Week worksheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    enroll_worksheet = sheet.worksheet("Enroll")
    week_worksheet = sheet.worksheet("Week")

    # Fetch data from Enroll and Week sheets
    enroll_data = enroll_worksheet.get_all_records()
    enroll_df = pd.DataFrame(enroll_data)
    week_data = week_worksheet.get_all_records()
    week_df = pd.DataFrame(week_data)

    # Collect changes for batch update
    changes = []

    # Display each class with its enrollment date
    for i, row in enroll_df.iterrows():
        class_name = row['Class Name']
        class_id = row['Class ID']
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
        formatted_date = new_date.strftime("%Y.%m.%d")  # Updated format to YYYY.MM.DD
        
        # Only add to changes if the date has changed
        if formatted_date != current_date:
            # Calculate weekly dates in the required format
            weekly_dates = [new_date + timedelta(weeks=j) for j in range(4)]
            formatted_weekly_dates = [d.strftime("%Y.%m.%d") for d in weekly_dates]  # Format as YYYY.MM.DD

            # Find the row in the Week sheet for this class
            week_row = week_df.index[week_df['Class ID'] == class_id].tolist()
            if week_row:
                row_index = week_row[0] + 2  # Adjust for header row in Google Sheets
                
                # Add to changes: the Date in Enroll and weekly dates in Week
                changes.append({
                    "enroll_row": i + 2,  # Adjust for header row in Enroll sheet
                    "week_row": row_index,
                    "Date": formatted_date,
                    "Weekly Dates": formatted_weekly_dates
                })
    
    # Submit button to save all changes
    if st.button("Submit All Changes"):
        for change in changes:
            # Update Enroll sheet with the new enrollment date
            enroll_worksheet.update_cell(change["enroll_row"], 3, change["Date"])  # Date column in Enroll sheet
            
            # Update Week sheet with calculated weekly dates
            for j, weekly_date in enumerate(change["Weekly Dates"], start=4):  # Weeks start from column 4 in Week sheet
                week_worksheet.update_cell(change["week_row"], j, weekly_date)
        
        st.success("Enrollment dates and weekly schedules updated successfully!")

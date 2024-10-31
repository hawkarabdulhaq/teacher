import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def update_post_dates():
    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    
    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Week and Post worksheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    week_worksheet = sheet.worksheet("Week")
    post_worksheet = sheet.worksheet("Post")

    # Fetch data from Week and Post sheets
    week_data = week_worksheet.get_all_records()
    week_df = pd.DataFrame(week_data)
    post_data = post_worksheet.get_all_records()
    post_df = pd.DataFrame(post_data)

    # Determine the current week based on the 'Week' column in the Post tab
    current_week_col = post_df.columns[0]  # Assuming "Week 1" is in the first column of Post
    week_num = post_df[current_week_col][0]  # Get the week number, e.g., "1" for "Week 1"

    # Map the current week number to the appropriate column in the Week tab
    week_column = f"Week {week_num}"  # Maps to columns like 'Week 1', 'Week 2', etc.

    # Loop through each row in the Post tab to apply the correct dates
    for i, post_row in post_df.iterrows():
        # Check if the row's week matches the current week
        if post_row[current_week_col] == week_num:
            # Loop through each class starting from the relevant columns (e.g., column 'G' onward)
            for class_name in post_df.columns[5:]:
                # Find the corresponding class row in the Week tab
                week_row = week_df[week_df['Class Name'] == class_name]
                
                # Only update if the week_row exists and has the correct week column
                if not week_row.empty and week_column in week_row.columns:
                    # Get the date for the current week for this class
                    date_value = week_row.iloc[0][week_column]
                    
                    # Get the row index and column index in the Post sheet
                    post_row_index = i + 2  # Adjust for header row in Google Sheets
                    class_col_index = post_df.columns.get_loc(class_name) + 1  # Column index to update
                    
                    # Update the cell in the Post tab
                    post_worksheet.update_cell(post_row_index, class_col_index, date_value)

    st.success("Post dates updated successfully for all rows in the current week!")

# Call the function to update post dates
update_post_dates()

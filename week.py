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

    # Collect updates for each class based on current week
    updates = []
    for class_name in post_df.columns[5:]:  # Start from column G onward
        # Find the row in the Week tab for this class
        week_row = week_df[week_df['Class Name'] == class_name]
        if not week_row.empty and week_column in week_row.columns:
            # Get the date for the current week for this class
            date_value = week_row.iloc[0][week_column]
            # Find the row index in Post tab to update
            post_row_index = post_df.index[post_df['Week 1'] == week_num].tolist()
            if post_row_index:
                post_row = post_row_index[0] + 2  # Adjust for header row in Google Sheets
                col_index = post_df.columns.get_loc(class_name) + 1  # Column index to update
                updates.append({
                    "row": post_row,
                    "col": col_index,
                    "date": date_value
                })

    # Apply all updates in one batch
    for update in updates:
        post_worksheet.update_cell(update["row"], update["col"], update["date"])
    st.success("Post dates updated successfully for the current week!")

# Call the function to update post dates
update_post_dates()

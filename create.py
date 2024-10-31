import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def show_create_dashboard():
    st.title("Create & Modify Course Content")
    st.write("Organized by week, this dashboard allows you to modify existing content, move entries, and add new entries for each week.")

    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    # Use Streamlit secrets for credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load Content worksheet
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    content_worksheet = sheet.worksheet("Content")

    # Fetch data
    data = content_worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Queue for batched updates
    updates = []

    # Group data by Week
    st.subheader("Modify Existing Content by Week")
    for week in sorted(df['Week'].unique()):
        week_data = df[df['Week'] == week]
        
        # Collapsible section for each week
        with st.expander(f"Week {week}"):
            for i, row in week_data.iterrows():
                st.write(f"**{row['Type']} - {row['Title']}**")
                
                # Editable fields for each entry
                content_type = st.selectbox(f"Type (Week {week}, Entry {i+1})", ["Material", "Assignment", "Question"], index=["Material", "Assignment", "Question"].index(row['Type']), key=f"type_{week}_{i}")
                title = st.text_input(f"Title (Week {week}, Entry {i+1})", value=row['Title'], key=f"title_{week}_{i}")
                content = st.text_area(f"Content (Week {week}, Entry {i+1})", value=row['Content'], key=f"content_{week}_{i}")
                link = st.text_input(f"Link (Week {week}, Entry {i+1})", value=row['Link'], key=f"link_{week}_{i}")

                # Calculate the correct row index in Google Sheets (adjusted for header row)
                row_index = df.index[df['Title'] == row['Title']].tolist()[0] + 2  # +2 to account for header and 0-based indexing

                # Queue the update instead of directly saving
                if st.button(f"Queue Changes for Entry {i+1} (Week {week})", key=f"queue_{week}_{i}"):
                    updates.append((row_index, content_type, title, content, link))
                    st.info(f"Changes for Entry {i+1} have been added to the queue.")

                st.write("---")

    # Button to submit all queued updates
    if st.button("Submit All Changes"):
        for row_index, content_type, title, content, link in updates:
            # Batch update queued rows
            content_worksheet.update_cell(row_index, 2, content_type)
            content_worksheet.update_cell(row_index, 3, title)
            content_worksheet.update_cell(row_index, 4, content)
            content_worksheet.update_cell(row_index, 5, link)
            time.sleep(1)  # Add a delay to avoid hitting API limits
        st.success("All changes have been successfully submitted!")
        updates.clear()  # Clear the queue after updates

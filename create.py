import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_create_dashboard():
    st.title("Create & Modify Course Content")
    st.write("Organized by week, this dashboard allows you to modify existing content, reorder entries, and add new entries for each week.")

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

    # Collect changes in a dictionary
    changes = []
    new_entries = []  # Separate collection for new entries

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

                # Store the changes for batch updating
                changes.append({
                    "row": row_index,
                    "Type": content_type,
                    "Title": title,
                    "Content": content,
                    "Link": link
                })

                # Move Up button (swap rows and collect changes)
                if i > 0 and st.button(f"Move Up (Entry {i+1})", key=f"move_up_{week}_{i}"):
                    swap_rows(content_worksheet, row_index, row_index - 1)
                    st.success("Moved entry up (pending submission)")

                # Move Down button (swap rows and collect changes)
                if i < len(week_data) - 1 and st.button(f"Move Down (Entry {i+1})", key=f"move_down_{week}_{i}"):
                    swap_rows(content_worksheet, row_index, row_index + 1)
                    st.success("Moved entry down (pending submission)")

                st.write("---")

            # Add new entry within this week
            st.write(f"### Add New Entry for Week {week}")
            new_type = st.selectbox(f"Type (New Entry, Week {week})", ["Material", "Assignment", "Question"], key=f"new_type_{week}")
            new_title = st.text_input(f"Title (New Entry, Week {week})", key=f"new_title_{week}")
            new_content = st.text_area(f"Content (New Entry, Week {week})", key=f"new_content_{week}")
            new_link = st.text_input(f"Link (New Entry, Week {week})", key=f"new_link_{week}")

            # Collect new entry data for batch submission
            if st.button(f"Add New Entry to Week {week}", key=f"add_{week}"):
                new_entries.append([week, new_type, new_title, new_content, new_link])
                st.success(f"New entry added to Week {week} (pending submission)")

    # Submit All Changes button with batch processing
    if st.button("Submit All Changes"):
        # Batch update for existing entries
        if changes:
            batch_updates = []
            for change in changes:
                # Set the range from column B (Type) to column E (Link) for the correct row
                batch_updates.append({
                    "range": f"B{change['row']}:E{change['row']}",
                    "values": [[change["Type"], change["Title"], change["Content"], change["Link"]]]
                })
            content_worksheet.batch_update(batch_updates)
            st.success("All updates applied successfully.")

        # Batch append new entries
        if new_entries:
            content_worksheet.append_rows(new_entries)
            st.success("All new entries added successfully.")
            
        # Clear changes and new_entries after submission
        changes.clear()
        new_entries.clear()

def swap_rows(worksheet, row1, row2):
    """Helper function to swap two rows in the Google Sheets worksheet."""
    row1_data = worksheet.row_values(row1)
    row2_data = worksheet.row_values(row2)
    
    # Swap the rows
    worksheet.update(f"A{row1}:E{row1}", [row2_data])
    worksheet.update(f"A{row2}:E{row2}", [row1_data])

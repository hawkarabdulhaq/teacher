import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_create_dashboard():
    st.title("Create & Modify Course Content")
    st.write("Organized by week, this dashboard allows you to modify existing content and add new entries for each week.")

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

                # Button to save changes for this entry
                if st.button(f"Save Changes (Week {week}, Entry {i+1})", key=f"save_{week}_{i}"):
                    # Find the exact row in Google Sheets and update
                    row_index = week_data.index[i] + 2  # +2 to account for header and zero indexing
                    content_worksheet.update_cell(row_index, 2, content_type)
                    content_worksheet.update_cell(row_index, 3, title)
                    content_worksheet.update_cell(row_index, 4, content)
                    content_worksheet.update_cell(row_index, 5, link)
                    st.success(f"Entry for Week {week} updated successfully!")
                st.write("---")

            # Add new entry within this week
            st.write(f"### Add New Entry for Week {week}")
            new_type = st.selectbox(f"Type (New Entry, Week {week})", ["Material", "Assignment", "Question"], key=f"new_type_{week}")
            new_title = st.text_input(f"Title (New Entry, Week {week})", key=f"new_title_{week}")
            new_content = st.text_area(f"Content (New Entry, Week {week})", key=f"new_content_{week}")
            new_link = st.text_input(f"Link (New Entry, Week {week})", key=f"new_link_{week}")

            # Button to add new entry for this week
            if st.button(f"Add New Entry to Week {week}", key=f"add_{week}"):
                content_worksheet.append_row([week, new_type, new_title, new_content, new_link])
                st.success(f"New entry added to Week {week} successfully!")

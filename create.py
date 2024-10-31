import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_create_dashboard():
    st.title("Create & Modify Content")
    st.write("Here, you can modify the existing content or add new entries to the Content tab.")

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

    # Display current content for editing
    st.subheader("Modify Existing Content")
    for i, row in df.iterrows():
        st.write(f"### Row {i+1}")
        
        # Editable fields
        week = st.number_input(f"Week (Row {i+1})", value=row['Week'], key=f"week_{i}")
        content_type = st.selectbox(f"Type (Row {i+1})", ["Material", "Assignment", "Question"], index=["Material", "Assignment", "Question"].index(row['Type']), key=f"type_{i}")
        title = st.text_input(f"Title (Row {i+1})", value=row['Title'], key=f"title_{i}")
        content = st.text_area(f"Content (Row {i+1})", value=row['Content'], key=f"content_{i}")
        link = st.text_input(f"Link (Row {i+1})", value=row['Link'], key=f"link_{i}")

        # Save changes to this row
        if st.button(f"Save Row {i+1}", key=f"save_{i}"):
            content_worksheet.update_cell(i + 2, 1, week)
            content_worksheet.update_cell(i + 2, 2, content_type)
            content_worksheet.update_cell(i + 2, 3, title)
            content_worksheet.update_cell(i + 2, 4, content)
            content_worksheet.update_cell(i + 2, 5, link)
            st.success(f"Row {i+1} updated successfully!")

    # Add a new row
    st.subheader("Add New Content")
    new_week = st.number_input("Week", min_value=1, step=1, key="new_week")
    new_type = st.selectbox("Type", ["Material", "Assignment", "Question"], key="new_type")
    new_title = st.text_input("Title", key="new_title")
    new_content = st.text_area("Content", key="new_content")
    new_link = st.text_input("Link", key="new_link")

    if st.button("Add New Row"):
        # Append the new row at the end of the worksheet
        content_worksheet.append_row([new_week, new_type, new_title, new_content, new_link])
        st.success("New row added successfully!")

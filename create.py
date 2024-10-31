import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def show_create_dashboard():
    st.title("Create Dashboard")
    st.write("Modify the content table directly from here.")

    # Google Sheets API setup
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load the 'Content' worksheet
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    worksheet = sheet.worksheet("Content")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Display the content table with editable fields
    st.subheader("Edit Existing Content")
    edited_df = pd.DataFrame()

    # Collect user edits for each cell in a form
    with st.form("edit_form"):
        for index, row in df.iterrows():
            st.write(f"### Row {index + 1}")
            edited_row = {}
            for col in df.columns:
                edited_row[col] = st.text_input(f"{col}", value=row[col])
            edited_df = edited_df.append(edited_row, ignore_index=True)

        # Update button
        submit_edit = st.form_submit_button("Update Table")

    # Update the Google Sheet if edits were submitted
    if submit_edit:
        worksheet.clear()  # Clear existing data
        worksheet.update([df.columns.values.tolist()] + edited_df.values.tolist())
        st.success("Table updated successfully!")
    
    # Section to add a new row
    st.subheader("Add New Row")
    new_row_data = {}
    for col in df.columns:
        new_row_data[col] = st.text_input(f"New {col}")
    
    if st.button("Add Row"):
        new_row = [new_row_data[col] for col in df.columns]
        worksheet.append_row(new_row)
        st.success("New row added successfully!")

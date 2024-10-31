import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API setup using Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]

# Load the Google Sheets API credentials from Streamlit secrets
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)

# Load data from Google Sheets
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
worksheet = sheet.worksheet("Content")
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Streamlit app layout
st.title("Teacher Dashboard: Course Content")

# Display each week’s content in a single collapsible section
for week in sorted(df['Week'].unique()):
    with st.expander(f"Week {week}"):
        weekly_data = df[df['Week'] == week]

        # Loop through each row within the selected week
        for _, row in weekly_data.iterrows():
            # Add type label as a badge or header to distinguish content
            if row['Type'] == "Material":
                st.markdown("#### 📘 Material")
            elif row['Type'] == "Assignment":
                st.markdown("#### 📝 Assignment")
            elif row['Type'] == "Question":
                st.markdown("#### ❓ Question")
            
            # Display title, content, and link
            st.write(f"**{row['Title']}**")
            st.write(row['Content'])
            if row['Link']:
                st.write(f"[View Resource]({row['Link']})")
            st.write("---")  # Separator between entries

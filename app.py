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
worksheet = sheet.worksheet("content")
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Streamlit app layout
st.title("Teacher Dashboard: Course Content")

# Sidebar with weeks navigation
st.sidebar.header("Select Week")
selected_week = st.sidebar.selectbox("Week", sorted(df['Week'].unique()))

# Display each week’s content in collapsible sections
for week in sorted(df['Week'].unique()):
    with st.expander(f"Week {week}", expanded=(week == selected_week)):
        weekly_data = df[df['Week'] == week]
        
        # Tabs for content type
        tab_materials, tab_assignments, tab_questions = st.tabs(["Materials", "Assignments", "Questions"])
        
        # Display Materials
        with tab_materials:
            materials = weekly_data[weekly_data['Type'] == "Material"]
            for _, row in materials.iterrows():
                st.write(f"**{row['Title']}**")
                st.write(row['Content'])
                if row['Link']:
                    st.write(f"[View Resource]({row['Link']})")
                st.write("---")
        
        # Display Assignments
        with tab_assignments:
            assignments = weekly_data[weekly_data['Type'] == "Assignment"]
            for _, row in assignments.iterrows():
                st.write(f"**{row['Title']}**")
                st.write(row['Content'])
                if row['Link']:
                    st.write(f"[View Resource]({row['Link']})")
                st.write("---")
        
        # Display Questions
        with tab_questions:
            questions = weekly_data[weekly_data['Type'] == "Question"]
            for _, row in questions.iterrows():
                st.write(f"**{row['Title']}**")
                st.write(row['Content'])
                if row['Link']:
                    st.write(f"[View Resource]({row['Link']})")
                st.write("---")

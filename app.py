import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from students import show_student_dashboard  # Import the student dashboard function

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

# Sidebar for navigation
st.sidebar.title("Navigation")
view_choice = st.sidebar.radio("Go to", ["Content", "Students"])

# Show Content or Students view based on sidebar selection
if view_choice == "Content":
    # Display course content (from your original content code)
    st.title("Teacher Dashboard: Course Content")

    selected_week = st.sidebar.selectbox("Week", sorted(df['Week'].unique()))

    for week in sorted(df['Week'].unique()):
        with st.expander(f"Week {week}", expanded=(week == selected_week)):
            weekly_data = df[df['Week'] == week]

            for _, row in weekly_data.iterrows():
                if row['Type'] == "Material":
                    st.markdown("#### 📘 Material")
                elif row['Type'] == "Assignment":
                    st.markdown("#### 📝 Assignment")
                elif row['Type'] == "Question":
                    st.markdown("#### ❓ Question")
                
                st.write(f"**{row['Title']}**")
                st.write(row['Content'])
                if row['Link']:
                    st.write(f"[View Resource]({row['Link']})")
                st.write("---")

elif view_choice == "Students":
    # Call the student dashboard function
    show_student_dashboard()

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

# Sidebar Navigation
st.sidebar.title("Navigation")
page_choice = st.sidebar.radio("Select Page", ["Content", "Students"])

# Display Content or Students page based on selection
if page_choice == "Content":
    # Display course content
    st.title("Course Content")

    # Loop through each week and show all types of content together
    for week in sorted(df['Week'].unique()):
        with st.expander(f"Week {week}"):
            weekly_data = df[df['Week'] == week]

            for _, row in weekly_data.iterrows():
                # Type label for each content piece
                if row['Type'] == "Material":
                    st.markdown("#### 📘 Material")
                elif row['Type'] == "Assignment":
                    st.markdown("#### 📝 Assignment")
                elif row['Type'] == "Question":
                    st.markdown("#### ❓ Question")
                
                # Display content details
                st.write(f"**{row['Title']}**")
                st.write(row['Content'])
                if row['Link']:
                    st.write(f"[View Resource]({row['Link']})")
                st.write("---")  # Separator between entries

elif page_choice == "Students":
    # Call the student dashboard function
    show_student_dashboard()

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
st.title("E-Learning Content Dashboard")

# Sidebar navigation
st.sidebar.header("Navigation")
selected_week = st.sidebar.selectbox("Select Week", sorted(df['Week'].unique()))
selected_type = st.sidebar.selectbox("Select Content Type", sorted(df['Type'].unique()))

# Filter data by week and content type
filtered_data = df[(df['Week'] == selected_week) & (df['Type'] == selected_type)]

# Display content
st.subheader(f"Week {selected_week} - {selected_type} Content")

for _, row in filtered_data.iterrows():
    st.write(f"### {row['Title']}")
    st.write(row['Content'])
    if row['Link']:
        st.write(f"[View Resource]({row['Link']})")
    st.write("---")

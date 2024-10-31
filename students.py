import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def load_student_data():
    # Google Sheets API setup using Streamlit secrets
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]

    # Load credentials from Streamlit secrets
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(credentials)

    # Load data from Google Sheets
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IWn53fkhx_rznRJOGLqx-HlxOz7dffq6WiO_BRYe1aM/edit#gid=171068923")
    student_worksheet = sheet.worksheet("Students")  # Update this to your actual worksheet name if different
    content_worksheet = sheet.worksheet("Content")

    # Load data into DataFrames
    student_data = pd.DataFrame(student_worksheet.get_all_records())
    content_data = pd.DataFrame(content_worksheet.get_all_records())
    
    return student_data, content_data

def show_student_dashboard():
    st.title("Student Dashboard")
    
    # Load student and content data
    student_data, content_data = load_student_data()

    # Get unique classes from student data
    classes = student_data['Class Name'].unique()
    
    # Display each class as a collapsible section
    for class_name in classes:
        with st.expander(f"Class: {class_name}"):
            # Filter students by class
            class_students = student_data[student_data['Class Name'] == class_name]

            # Display students in the class
            st.subheader("Students")
            for _, student in class_students.iterrows():
                st.write(f"**{student['Student Name']}** - ID: {student['Student ID']}")

            # Display course content for the class
            st.subheader("Course Content")
            class_content = content_data  # Assuming all content applies to all classes
            
            # Loop through each week and display content
            for week in sorted(class_content['Week'].unique()):
                with st.expander(f"Week {week}"):
                    weekly_data = class_content[class_content['Week'] == week]

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


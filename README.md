# Project: Flask-Based Face Recognition Attendance System
# Project Overview
-> This is a Flask-based face recognition attendance system where users can register with their photos, and the system captures attendance using a webcam by matching 
   faces with registered users. Attendance is recorded in an Excel sheet.
 # Workflow
1️. User Registration -->
                User enters their name and uploads a photo.
                The system saves the photo and extracts facial features.
2️. Attendance Marking -->
               The system opens the webcam to capture an image.
               It detects faces and compares them with registered users.
               If a match is found, the name and timestamp are recorded in attendance.xlsx.
3️. Attendance Report-->
               The attendance sheet contains Name, Date, and Time of each marked attendance.


from flask import Flask, render_template, request, redirect, url_for
import cv2
import os
import numpy as np
import pandas as pd
import face_recognition
from datetime import datetime
from flask import send_file

app = Flask(__name__)

# Directory to store user images
IMAGE_DIR = 'static/photos'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Path to attendance Excel file
ATTENDANCE_FILE = 'attendance.xlsx'

# Load known face encodings and names
def load_known_faces():
    known_encodings = []
    known_names = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(IMAGE_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])
    return known_encodings, known_names

known_face_encodings, known_face_names = load_known_faces()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['image']
        if name and file:
            filename = f"{name}.jpg"
            file_path = os.path.join(IMAGE_DIR, filename)
            file.save(file_path)
            # Update known faces
            global known_face_encodings, known_face_names
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(name)
            return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            return "Error: Unable to access the camera"
        ret, frame = video_capture.read()
        video_capture.release()
        if not ret:
            return "Failed to capture image"
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        attendees = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            attendees.append(name)
        # Record attendance
        if os.path.exists(ATTENDANCE_FILE):
            df = pd.read_excel(ATTENDANCE_FILE)
        else:
            df = pd.DataFrame(columns=['Name', 'Date', 'Time'])
        for attendee in attendees:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            if not ((df['Name'] == attendee) & (df['Date'] == date_str)).any():
                df = pd.concat([df,pd.DataFrame({'Name': [attendee], 'Date': [date_str], 'Time': [time_str]})], ignore_index=True)
        df.to_excel(ATTENDANCE_FILE, index=False)
        return render_template('attendance.html', attendees=attendees)
    return render_template('attendance.html', attendees=[])

@app.route('/download')
def download_attendance():
    return send_file(ATTENDANCE_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
# from flask import Flask, render_template, request, jsonify
# import tensorflow as tf
# import numpy as np
# import cv2 as cv
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Load and preprocess MNIST dataset
# mnist = tf.keras.datasets.mnist
# (x_train, y_train), (x_test, y_test) = mnist.load_data()
# x_train = tf.keras.utils.normalize(x_train, axis=1)
# x_test = tf.keras.utils.normalize(x_test, axis=1)

# # Define the model
# model = tf.keras.models.Sequential([
#     tf.keras.layers.Flatten(input_shape=(28, 28)),
#     tf.keras.layers.Dense(128, activation='relu'),
#     tf.keras.layers.Dense(128, activation='relu'),
#     tf.keras.layers.Dense(10, activation='softmax')
# ])

# # Compile and train the model
# model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
# model.fit(x_train, y_train, epochs=3)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     file = request.files['file']
#     if file:
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         img = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
#         img = cv.resize(img, (28, 28))
#         img = np.invert(img)
#         img = img / 255.0
#         img = np.array([img])
        
#         prediction = model.predict(img)
#         digit = np.argmax(prediction)
        
#         return jsonify({'digit': int(digit)})
#     return jsonify({'error': 'No file uploaded'})

# if __name__ == '__main__':
#     app.run(debug=True)

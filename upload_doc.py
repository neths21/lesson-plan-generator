# from flask import Flask, request, jsonify
# import os

# app = Flask(__name__)
# UPLOAD_FOLDER = 'C:/uploaded'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'files' not in request.files:
#         return "No file part", 400
    
#     files = request.files.getlist('files')
    
#     for file in files:
#         if file.filename:
#             file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    
#     return "Files uploaded successfully!", 200

# if __name__ == '__main__':
#     app.run(debug=True)
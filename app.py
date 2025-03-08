from flask import Flask, render_template, request, jsonify
import os
from pypdf import PdfReader
import google.generativeai as genai
import sys
from flask_sqlalchemy import SQLAlchemy

# Force UTF-8 encoding for proper Unicode support
sys.stdout.reconfigure(encoding='utf-8')
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:barbie@localhost/students_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    unit1 = db.Column(db.Integer, nullable=False)
    unit2 = db.Column(db.Integer, nullable=False)
    unit3 = db.Column(db.Integer, nullable=False)
    unit4 = db.Column(db.Integer, nullable=False)
    unit5 = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(2), nullable=False)



UPLOAD_FOLDER = r'D:\code\lesson_plan_generator\uploaded'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Google AI SDK
GOOGLE_API_KEY = "AIzaSyCMRmlBhSry38aigqjS3H1fzxj4KjHLfaQ"
genai.configure(api_key=GOOGLE_API_KEY)

for model in genai.list_models():
    print(model.name)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        print(f"\nPDF Loaded Successfully: {pdf_path}")
        print(f"Total Pages: {len(reader.pages)}")
        
        data = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                data += text
        
        return data.strip() if data else None
    except Exception as e:
        print(f"\nError reading PDF: {e}")
        return None

def generate_lesson_plan(syllabus_text, custom_prompt):
    """Generates a structured lesson plan using Google's Gemini AI."""
    prompt = f"""
    {custom_prompt}

    *Syllabus:*
    {syllabus_text[:4000]}  # Limiting input to 4000 characters

    *Lesson Plan Format:*
    - *Grade Level*: Identify the appropriate grade level.
    - *Topic*: Identify the main topic covered.
    - *Lesson Duration*: Suggest an appropriate duration.
    - *Learning Objectives*: Summarize key learning objectives.
    - *Lesson Structure*:
        1. *Introduction*: Briefly introduce the topic.
        2. *Main Activities*: Suggest engaging teaching methods.
        3. *Assessments*: Describe assessment techniques.
        4. *Conclusion*: Summarize key takeaways.

    Ensure the lesson is interactive and engaging.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else "Error generating lesson plan."
@app.route("/", methods=["GET"])
def home():
    return render_template("dashboard.html",students=Student.query.all())
@app.route("/students_analysis", methods=["GET"])
def students_analysis():
    students = Student.query.all()

    if not students:
        return jsonify({"message": "No students found."}), 404

    study_materials = {
        "mechanics": "https://www.khanacademy.org/science/physics/mechanics",
        "thermodynamics": "https://www.khanacademy.org/science/physics/thermodynamics",
        "electromagnetism": "https://www.khanacademy.org/science/physics/electromagnetism",
        "optics": "https://www.khanacademy.org/science/physics/light-and-optics",
        "electricity": "https://www.khanacademy.org/science/physics/circuits",
    }

    student_data = []
    for student in students:
        scores = {
            "mechanics": student.unit1,
            "thermodynamics": student.unit2,
            "electromagnetism": student.unit3,
            "optics": student.unit4,
            "electricity": student.unit5,
        }

        weakest_unit = min(scores, key=scores.get)
        suggestion = study_materials.get(weakest_unit, "No study material available.")

        student_data.append({
            "Student ID": student.student_id,
            "Student Name": student.student_name,
            "Scores": scores,
            "Weakest Unit": weakest_unit.capitalize(),
            "Suggested Study Material": suggestion
        })

    return render_template("student_analysis.html", students=student_data)

@app.route("/lesson_plan", methods=["GET"])
def lesson_plan():

    return render_template("lesson_plan_generator.html")
@app.route("/test_report", methods=["GET"])
def test_report():
    return render_template("testreport.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'files' not in request.files:
        return "No file part", 400
    
    files = request.files.getlist('files')
    if not files:
        return "No files selected", 400
    
    file_paths = []
    try:
        for file in files:
            if file.filename:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                file_paths.append(file_path)
        return jsonify({"message": "Files uploaded successfully!", "file_paths": file_paths}), 200
    except Exception as e:
        return f"Upload failed: {str(e)}", 500

@app.route("/generate_lesson_plan", methods=["POST"])
def generate_plan():
    data = request.json
    custom_prompt = data.get("prompt", "").strip()

    # Fetch the latest uploaded file
    uploaded_files = os.listdir(UPLOAD_FOLDER)
    if not uploaded_files:
        return jsonify({"error": "No syllabus file uploaded."}), 400
    
    latest_file = max(uploaded_files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_FOLDER, f)))
    file_path = os.path.join(UPLOAD_FOLDER, latest_file)
    
    syllabus_text = extract_text_from_pdf(file_path)
    if not syllabus_text:
        return jsonify({"error": "No text extracted from PDF."}), 400
    
    lesson_plan = generate_lesson_plan(syllabus_text, custom_prompt)
    return jsonify({"lesson_plan": lesson_plan})

if __name__ == "_main_":
    app.run(debug=True)
from pypdf import PdfReader
import google.generativeai as genai
import sys

# Force UTF-8 encoding for proper Unicode support
sys.stdout.reconfigure(encoding='utf-8')

# Set your Google AI API Key
GOOGLE_API_KEY = "AIzaSyCMRmlBhSry38aigqjS3H1fzxj4KjHLfaQ"  # Replace with your actual API key

# Configure Google AI SDK
genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        print(f"\nPDF Loaded Successfully: {pdf_path}")
        print(f"Total Pages: {len(reader.pages)}")  # Display total number of pages
        
        data = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                data += text
        
        return data.strip() if data else None  # Return cleaned text

    except Exception as e:
        print(f"\nError reading PDF: {e}")
        return None

def generate_lesson_plan(syllabus_text, custom_prompt):
    """Generates a structured lesson plan using Google's Gemini AI."""

    prompt = f"""
    {custom_prompt}

    Syllabus:
    {syllabus_text[:4000]}  # Limiting input to 4000 characters

    **Lesson Plan Format:**
    - **Grade Level**: Identify the appropriate grade level.
    - **Topic**: Identify the main topic covered.
    - **Lesson Duration**: Suggest an appropriate duration.
    - **Learning Objectives**: Summarize key learning objectives.
    - **Lesson Structure**:
        1. **Introduction**: Briefly introduce the topic.
        2. **Main Activities**: Suggest engaging teaching methods.
        3. **Assessments**: Describe assessment techniques.
        4. **Conclusion**: Summarize the key takeaways.

    Make the lesson interactive, engaging for students, and create a timeline to cover all the portions.
    """

    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)

    return response.text if response and hasattr(response, "text") else "Error generating lesson plan."

# Main Execution
#if __name__ == "__main__":
    # Get PDF file from user
pdf_path = input("Enter the PDF file name (including extension): ").strip()

    # Extract syllabus text from PDF
syllabus_text = extract_text_from_pdf(pdf_path)

if not syllabus_text:
    print("Error: No text extracted from PDF. Please check the file.")
else:
        # Get custom user prompt
    print("\nProvide a custom prompt to personalize the lesson plan:")
    custom_prompt = input("Enter your lesson plan instructions: ").strip()

        # Generate AI-powered lesson plan
lesson_plan = generate_lesson_plan(syllabus_text, custom_prompt)


print("\n*Generated Lesson Plan*\n")
print(lesson_plan)

import os
from flask import Flask, render_template, request, redirect, url_for
import resume_skills_extraction as resume_parser

app = Flask(__name__)

# Define the path for uploaded files
app.config['UPLOAD_FOLDER'] = 'resume_skills_extractor'  # Update the folder name here
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Check if the folder exists (optional but recommended)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # Process the uploaded resume
    name, skills = resume_parser.parse_resume(filepath)
    
    # Return the result to the user in the required format
    return render_template('result.html', name=name, skills=skills)

if __name__ == '__main__':
    app.run(debug=True)

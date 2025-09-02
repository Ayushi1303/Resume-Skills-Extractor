import re
import docx2txt
from PyPDF2 import PdfReader
import pdfplumber

# Skills database (same as your code)
SKILLS_DB = [
    "Python", "Java", "Machine Learning", "SQL", "C++", "HTML", "CSS", "JavaScript",
    "Bootstrap", "Tailwind", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Flask", "Django",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase",
    # Data Science & ML
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow", "Keras", "PyTorch", "Data Analysis",
    "Data Visualization", "Deep Learning", "Artificial Intelligence", "Natural Language Processing",
    # Tools & Platforms
    "Git", "GitHub", "Docker", "AWS", "Google Cloud", "Azure", "Jira", "VS Code", "Jupyter", "Linux", "Power BI", "Tableau",
    # Concepts
    "OOP", "DSA", "REST API", "Microservices", "Agile", "CI/CD", "Unit Testing", "Cloud Computing",
    # Soft Skills
    "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Creativity", "Critical Thinking"
]

UNWANTED_NAME_KEYWORDS = [
    "cgpa", "gpa", "percentage", "grade", "graduating", "year",
    "education", "university", "college", "institute", "school",
    "degree", "b.e", "btech", "mtech", "msc", "pursuing"
]

def extract_text_from_resume(file_path):
    """Extracts text from PDF or DOCX resume and saves to a .txt file."""
    if file_path.endswith('.pdf'):
        # Use pdfplumber for better extraction
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file type")
    # Save extracted text to file for debugging
    txt_path = file_path.rsplit('.', 1)[0] + "_extracted.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text

def extract_skills(text):
    """Extracts matching skills from resume text."""
    text = text.lower()
    return [skill for skill in SKILLS_DB if skill.lower() in text]

def extract_name(lines):
    """
    Extract candidate name from resume lines.
    Assumes name is the first word(s) before the address line (which usually contains numbers or address keywords).
    """
    address_keywords = ["street", "road", "lane", "city", "state", "pin", "pincode", "zip", "mobile", "contact", "email", "phone"]
    name_parts = []
    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue
        # If line looks like address, stop collecting name
        if any(kw in line.lower() for kw in address_keywords) or re.search(r'\d', line):
            break
        # If line is all uppercase or contains unwanted keywords, skip
        if line.isupper() or any(x in line.lower() for x in UNWANTED_NAME_KEYWORDS):
            continue
        # If line contains skills, skip
        if any(skill.lower() in line.lower() for skill in SKILLS_DB):
            continue
        name_parts.append(line)
        # If we have 1-2 lines, that's enough for a name
        if len(name_parts) >= 2:
            break
    if name_parts:
        return " ".join(name_parts)
    # Fallback: first non-empty line
    for line in lines[:10]:
        line = line.strip()
        if line:
            return line
    return "Name not found"

def parse_resume(filepath):
    """Main function to parse resume and extract name + skills."""
    resume_text = extract_text_from_resume(filepath)
    skills = extract_skills(resume_text)
    lines = resume_text.splitlines()
    name = extract_name(lines)
    return name, skills

# Example usage
if __name__ == "__main__":
    filepath = "college_resume_ayush.pdf"  # Update with your test file
    name, skills = parse_resume(filepath)
    print("Extracted Name:", name)
    print("Extracted Skills:", skills)

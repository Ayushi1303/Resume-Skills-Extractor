import os
from flask import Flask, render_template, request, redirect, url_for, session
import resume_skills_extraction as resume_parser
from utils.question_generator import generate_questions

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

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
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    session['uploaded_file'] = filepath
    # Redirect to analyzing page (shows spinner)
    return redirect(url_for('analyzing'))

@app.route('/analyzing')
def analyzing():
    filepath = session.get('uploaded_file', None)
    if not filepath:
        return redirect(url_for('index'))
    # Just show the spinner/loading page. Resume processing will be triggered by JS.
    return render_template('analyzing.html')

@app.route('/process_resume', methods=['POST'])
def process_resume():
    filepath = session.get('uploaded_file', None)
    if not filepath:
        return redirect(url_for('index'))
    name, skills = resume_parser.parse_resume(filepath)
    # Select top 5 skills
    selected_skills = skills[:5]
    quiz = []
    for skill in selected_skills:
        questions_text = generate_questions(skill)
        # Split into blocks, each block is a question
        for block in questions_text.strip().split('\n\n')[:5]:  # Take only 5 questions per skill
            lines = block.strip().split('\n')
            if len(lines) < 6 or not lines[5].startswith('Answer:'):
                continue
            answer_parts = lines[5].split(': ')
            if len(answer_parts) != 2:
                continue
            q = {
                'skill': skill,
                'question': lines[0][4:],
                'options': [l[3:] for l in lines[1:5]],
                'correct': answer_parts[1].strip()
            }
            quiz.append(q)
    session['quiz'] = quiz
    session['name'] = name
    session['skills'] = selected_skills
    # After processing, redirect to skills page
    return redirect(url_for('skills'))

@app.route('/skills')
def skills():
    name = session.get('name', '')
    skills = session.get('skills', [])
    if not skills:
        return redirect(url_for('index'))
    return render_template('skills.html', name=name, skills=skills)

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    name = session.get('name', '')
    quiz = session.get('quiz', [])
    if not quiz:
        return redirect(url_for('index'))
    return render_template('quiz.html', name=name, quiz=quiz)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    quiz = session.get('quiz', [])
    score = 0
    results = []
    missed_skills = []
    for i, q in enumerate(quiz):
        user_ans = request.form.get(f'q{i}')
        is_correct = (user_ans == q['correct'])
        results.append({'question': q['question'], 'your_answer': user_ans, 'correct_answer': q['correct'], 'is_correct': is_correct})
        if is_correct:
            score += 1
        else:
            missed_skills.append(q['question'])

    # Notes/Recommendations with links
    notes = []
    for skill in missed_skills:
        notes.append({
            "text": f"Review {skill} on GeeksforGeeks",
            "url": f"https://www.geeksforgeeks.org/?s={skill.replace(' ', '+')}"
        })
        notes.append({
            "text": f"{skill} course on Coursera",
            "url": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}"
        })
        notes.append({
            "text": f"Official documentation for {skill}",
            "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+official+documentation"
        })

    # Company recommendations with links
    if score == len(quiz):
        companies = [
            {"name": "Google", "url": "https://careers.google.com/jobs/results/"},
            {"name": "Microsoft", "url": "https://careers.microsoft.com/"},
            {"name": "Amazon", "url": "https://www.amazon.jobs/en/"},
            {"name": "Meta", "url": "https://www.metacareers.com/jobs"}
        ]
    elif score >= len(quiz) * 0.7:
        companies = [
            {"name": "TCS", "url": "https://www.tcs.com/careers"},
            {"name": "Infosys", "url": "https://www.infosys.com/careers/apply.html"},
            {"name": "Wipro", "url": "https://careers.wipro.com/"},
            {"name": "Accenture", "url": "https://www.accenture.com/in-en/careers"}
        ]
    else:
        companies = [
            {"name": "Internshala", "url": "https://internshala.com/internships/"},
            {"name": "AngelList Startups", "url": "https://angel.co/jobs"},
            {"name": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/"},
            {"name": "Coursera", "url": "https://www.coursera.org/"}
        ]

    return render_template('score.html', results=results, score=score, total=len(quiz), notes=notes, companies=companies)

@app.route('/retry')
def retry():
    quiz = session.get('quiz', [])
    name = session.get('name', '')
    return render_template('quiz.html', name=name, quiz=quiz)

if __name__ == '__main__':
    app.run(debug=True, port=5050)

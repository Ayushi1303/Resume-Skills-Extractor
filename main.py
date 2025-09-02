from utils.skill_extractor import extract_skills_from_csv
from utils.question_generator import generate_questions
from utils.quiz_runner import run_quiz

from dotenv import load_dotenv
import os
import resume_skills_extraction

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")  # For question generation if needed


def main():
    # Example integration: extract name and skills from a resume file using resume_skills_extraction
    resume_path = "college_resume_ayush.pdf"  # Change to your test file
    name, skills = resume_skills_extraction.parse_resume(resume_path)
    print(f"Extracted Name: {name}")
    print(f"Extracted Skills: {skills}")

    csv_path = "extracted_resume_data.csv"  # Your CSV with latest extracted skills

    # Always read the latest CSV data, taking top 5 skills per user
    try:
        users = extract_skills_from_csv(csv_path, top_n=5)  # ✅ top 5 skills
    except FileNotFoundError:
        print(f"⚠️ CSV file not found: {csv_path}")
        return

    # Loop through each user in the latest CSV
    for name, skills in users:
        if not skills:
            print(f"⚠️ No skills found for {name}. Skipping quiz.")
            continue

        print(f"\n👋 Welcome {name}!")
        print(f"📘 Skills selected for quiz (top {len(skills)}): {', '.join(skills)}")

        total_score = 0
        max_score = len(skills) * 5  # Each skill → 5 questions → max 5 points

        for skill in skills:
            print(f"\n🎯 Skill: {skill}\n")
            try:
                questions = generate_questions(skill)
                score = run_quiz(questions)   # ✅ run_quiz must return score
                total_score += score
            except Exception as e:
                print(f"⚠️ Error generating questions for {skill}: {e}")

        print(f"\n📝 Final Score for {name}: {total_score} / {max_score}")
        print("=" * 50)


if __name__ == "__main__":
    main()

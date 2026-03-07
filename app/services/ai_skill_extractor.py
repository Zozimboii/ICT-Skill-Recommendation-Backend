# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"))


# def extract_skills(description: str):

#     if not description.strip():
#         return {"hard_skills": [], "soft_skills": []}

#     prompt = f"""
#     Extract hard skills and soft skills from this job description.
#     Return ONLY valid JSON with no explanation.

#     {{
#         "hard_skills": [],
#         "soft_skills": []
#     }}

#     Job Description:
#     {description}
#     """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.2
#     )

#     content = response.choices[0].message.content.strip()

#     try:
#         return json.loads(content)
#     except:
#         return {"hard_skills": [], "soft_skills": []}




import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")
)


def extract_skills_with_ai(description: str):
    if not description or len(description) < 20:
        return {"hard_skills": [], "soft_skills": []}
    prompt = f"""
    You are an expert ICT job skill analyzer.
    
    Job Description:
    {description}
    
    Instructions:
    1. Extract only GENERAL and TRANSFERABLE Hard Skills and Soft Skills.
       - Do NOT include company-specific tools, internal systems, or overly niche requirements.
       - Focus on skills that are reusable across similar roles.
       - Keep skills concise (1-3 words per skill).
    
    2. Classify this job into ONE of the following ICT categories:
       [Software Development, Data Science & Analytics, IT Support, Network & Security, Project Management, Quality Assurance]
    
    Rules:
    - Do not guess beyond the given description.
    - If unsure, choose the closest matching category.
    - Return 5–10 hard skills and 3–6 soft skills.
    - Normalize similar skills.
    - Remove duplicated or overlapping skills.
    - Avoid listing specific programming frameworks unless core.
    - Prefer broader skill categories.
    
    Return ONLY valid JSON in this format:
    {{
      "sub_category": "Category Name",
      "hard_skills": ["Skill1", "Skill2"],
      "soft_skills": ["Skill1", "Skill2"]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
        return {"hard_skills": [], "soft_skills": []}
# def extract_skills(text: str):

#     if not text:
#         return {"hard_skills": [], "soft_skills": []}

#     prompt = f"""
#     Extract skills from this job description.

#     Return JSON format only like this:
#     {{
#         "hard_skills": ["Python", "SQL"],
#         "soft_skills": ["Communication", "Teamwork"]
#     }}

#     Job Description:
#     {text}
#     """

#     response = model.generate_content(prompt)

#     try:
#         data = json.loads(response.text)
#         return data
#     except:
#         return {"hard_skills": [], "soft_skills": []}


# def extract_skills(text: str):

#     if not text:
#         return {"hard_skills": [], "soft_skills": []}

#     prompt = f"""
# Extract skills from the job description.

# Return JSON ONLY in this format:
# {{
#   "hard_skills": [],
#   "soft_skills": []
# }}

# Job Description:
# {text}
# """

#     try:
#         response = model.generate_content(prompt)

#         if not response.text:
#             return {"hard_skills": [], "soft_skills": []}

#         clean = response.text.strip()

#         # remove markdown block if exists
#         if clean.startswith("```"):
#             clean = clean.replace("```json", "").replace("```", "").strip()

#         data = json.loads(clean)

#         return {
#             "hard_skills": data.get("hard_skills", []),
#             "soft_skills": data.get("soft_skills", []),
#         }

#     except Exception as e:
#         print("⚠️ AI parse error:", e)
#         return {"hard_skills": [], "soft_skills": []}
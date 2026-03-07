# import os
# import re
# import google.generativeai as genai
# import json

# class AIService:

#     def __init__(self):
#         genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#         self.model = genai.GenerativeModel(
#             os.getenv("GEMINI_MODEL")
#         )
#         self.MAX_AI_JOBS = 20
#         self.ai_counter = 0

#     def can_call_ai(self):
#         return self.ai_counter < self.MAX_AI_JOBS
    
#     def extract_skills(self, description: str):

#         try:
#             description = description[:3000]

#             prompt = f"""
#                 Act as a professional recruiter. Extract technical skills (hard_skills) and interpersonal skills (soft_skills) from the provided job descriptions.
    
#                 IMPORTANT: Return ONLY a valid JSON list of objects. No preamble, no explanation, no markdown blocks.

#                 Return JSON only:
#                 {{
#                   "hard_skills": [],
#                   "soft_skills": []
#                 }}

#                 Job Description:
#                 {description}
#                 """

#             response = self.model.generate_content(
#                 prompt,
#                 generation_config={"temperature": 0.2}
#             )

#             text = response.text.strip()
#             text = text.replace("```json", "").replace("```", "")
#             return json.loads(text)

#         except Exception as e:
#             print("AI ERROR:", e)
#             return {
#                 "hard_skills": [],
#                 "soft_skills": []
#             }
        
#     import json

#     def extract_batch_skills(self, descriptions: list):

#         # descriptions_json = json.dumps(descriptions, ensure_ascii=False)

#         prompt = f"""
#         You are a strict JSON generator.

#         Act as a professional recruiter. Extract technical skills (hard_skills) and interpersonal skills (soft_skills) from the provided job descriptions.
    
#         IMPORTANT: Return ONLY a valid JSON list of objects. No preamble, no explanation, no markdown blocks.

#         FORMAT:
#         [
#           {{
#             "hard_skills": ["Skill1", "Skill2"],
#             "soft_skills": ["SkillA", "SkillB"]
#           }}
#         ]
        
#         Job Descriptions:
#         {json.dumps(descriptions, ensure_ascii=False)} 
#         """

#         response = self.model.generate_content(
#             prompt,
#             generation_config={
#                 "temperature": 0.1, # ลดความสร้างสรรค์ลงเพื่อให้โครงสร้างคงที่
#                 "response_mime_type": "application/json" # บังคับ Output เป็น JSON
#             }
#         )

#         text = response.text.strip()
#         json_match = re.search(r'\[.*\]', text, re.DOTALL)
#         if json_match:
#             clean_text = json_match.group()
#         else:
#             clean_text = text

#         try:
#             return json.loads(clean_text)
#         except json.JSONDecodeError as e:
#             print(f"❌ JSON Error at: {clean_text[:100]}") # พิมพ์ดูว่ามันพังตรงไหน
#             # หากพัง อาจจะลอง return list ว่าง เพื่อไม่ให้ระบบหยุดทำงาน (Stop-gap)
#             return [{"hard_skills": [], "soft_skills": []} for _ in descriptions]
#         # return json.loads(text)
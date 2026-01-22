from pathlib import Path
import re

# ---- requirements.txt ----
req = Path('requirements.txt')
text = req.read_text(encoding='utf-8')
line = 'google-generativeai==0.8.5'
if line not in text:
    if not text.endswith('\n'):
        text += '\n'
    text += line + '\n'
    req.write_text(text, encoding='utf-8')

# ---- app/ai_service.py ----
ai_path = Path('app/ai_service.py')
ai = ai_path.read_text(encoding='utf-8')

# Ensure provider env vars
if 'AI_PROVIDER' not in ai:
    ai = ai.replace(
        'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")',
        'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")\n\n# à¹€à¸¥à¸·à¸­à¸ provider: openai | gemini\nAI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()\n\n# Gemini API key / model\nGEMINI_API_KEY = os.getenv("GEMINI_API_KEY")\nGEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")'
    )

# Add helpers (append after imports/env)
if 'def _has_provider_key' not in ai:
    helpers = r'''

def _has_provider_key(provider: str) -> bool:
    if provider == "gemini":
        return bool(GEMINI_API_KEY)
    return bool(OPENAI_API_KEY)


def _summarize_with_openai(question: str, db_answer: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = """à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
à¸„à¸¸à¸“à¹„à¸”à¹‰à¸£à¸±à¸šà¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸ˆà¸³à¸™à¸§à¸™à¸‡à¸²à¸™à¸—à¸µà¹ˆà¸•à¹‰à¸­à¸‡à¸à¸²à¸£à¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰
à¸Šà¹ˆà¸§à¸¢à¸ªà¸£à¸¸à¸›à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£"""

    user_message = f"""à¸„à¸³à¸–à¸²à¸¡: {question}

à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥:
{db_answer}

à¸à¸£à¸¸à¸“à¸²à¸ªà¸£à¸¸à¸›à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸‚à¹‰à¸²à¸‡à¸•à¹‰à¸™à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def _summarize_with_gemini(question: str, db_answer: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT

à¸„à¸³à¸–à¸²à¸¡: {question}

à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥:
{db_answer}

à¸à¸£à¸¸à¸“à¸²à¸ªà¸£à¸¸à¸›à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸‚à¹‰à¸²à¸‡à¸•à¹‰à¸™à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰ (à¸•à¸­à¸šà¸ à¸²à¸©à¸²à¹„à¸—à¸¢ à¸à¸£à¸°à¸Šà¸±à¸š à¸Šà¸±à¸”à¹€à¸ˆà¸™)"""

    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    return (getattr(resp, "text", "") or "").strip()


def _general_chat_with_openai(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = """à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT (Information and Communication Technology)
à¸„à¸¸à¸“à¸Šà¹ˆà¸§à¸¢à¸•à¸­à¸šà¸„à¸³à¸–à¸²à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸š:
- à¸—à¸±à¸à¸©à¸°à¸—à¸µà¹ˆà¸ˆà¸³à¹€à¸›à¹‡à¸™à¸ªà¸³à¸«à¸£à¸±à¸šà¸­à¸²à¸Šà¸µà¸žà¸•à¹ˆà¸²à¸‡à¹† à¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
- à¹à¸™à¸°à¸™à¸³à¸—à¸±à¸à¸©à¸°à¸—à¸µà¹ˆà¸„à¸§à¸£à¹€à¸£à¸µà¸¢à¸™à¸£à¸¹à¹‰
- à¹€à¸—à¸£à¸™à¸”à¹Œà¸‚à¸­à¸‡à¸—à¸±à¸à¸©à¸°à¹ƒà¸™à¸•à¸¥à¸²à¸”à¸‡à¸²à¸™
- à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸à¸²à¸£à¸žà¸±à¸’à¸™à¸²à¸—à¸±à¸à¸©à¸°à¸­à¸²à¸Šà¸µà¸ž

à¸•à¸­à¸šà¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def _general_chat_with_gemini(question: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
à¸•à¸­à¸šà¸„à¸³à¸–à¸²à¸¡à¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£

à¸„à¸³à¸–à¸²à¸¡: {question}"""

    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    return (getattr(resp, "text", "") or "").strip()
'''
    # Insert helpers just before get_ai_response
    pos = ai.find('def get_ai_response(')
    if pos != -1:
        ai = ai[:pos] + helpers + '\n' + ai[pos:]

# Update key-check logic
ai = ai.replace('if not use_ai or not OPENAI_API_KEY:', 'if not use_ai or not _has_provider_key(AI_PROVIDER):')
ai = ai.replace('if not OPENAI_API_KEY or not use_ai:', 'if not use_ai or not _has_provider_key(AI_PROVIDER):')

# Route db-summary AI call (pattern-based)
ai = re.sub(
    r"# à¹ƒà¸Šà¹‰ AI à¸Šà¹ˆà¸§à¸¢à¸ªà¸£à¸¸à¸›à¹à¸¥à¸°à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡\s*\n\s*try:\s*\n\s*(?:from openai[\s\S]*?)?ai_summary\s*=\s*response\.choices\[0\]\.message\.content\.strip\(\)",
    "# à¹ƒà¸Šà¹‰ AI à¸Šà¹ˆà¸§à¸¢à¸ªà¸£à¸¸à¸›à¹à¸¥à¸°à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡\n        try:\n            if AI_PROVIDER == \"gemini\":\n                ai_summary = _summarize_with_gemini(question, db_answer)\n            else:\n                ai_summary = _summarize_with_openai(question, db_answer)",
    ai,
    count=1,
)

# Route general-chat AI call (pattern-based)
ai = re.sub(
    r"try:\s*\n\s*from openai[\s\S]*?return response\.choices\[0\]\.message\.content\.strip\(\)",
    "try:\n        if AI_PROVIDER == \"gemini\":\n            return _general_chat_with_gemini(question)\n        return _general_chat_with_openai(question)",
    ai,
    count=1,
)

ai_path.write_text(ai, encoding='utf-8')

# ---- app/main.py (has_ai should match provider key) ----
main_path = Path('app/main.py')
main = main_path.read_text(encoding='utf-8')
main = main.replace(
    'use_ai = bool(os.getenv("OPENAI_API_KEY"))',
    'provider = os.getenv("AI_PROVIDER", "openai").lower()\n    use_ai = bool(os.getenv("GEMINI_API_KEY")) if provider == "gemini" else bool(os.getenv("OPENAI_API_KEY"))'
)
main_path.write_text(main, encoding='utf-8')

print('OK: Gemini support added')

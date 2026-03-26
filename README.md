# ICT Skill Advisor — Backend

FastAPI backend สำหรับระบบวิเคราะห์ทักษะและแนะนำงาน ICT ไทย

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM
- **MySQL** — ฐานข้อมูล
- **Google Gemini** — AI สำหรับ extract skills และ classify งาน
- **Playwright + BeautifulSoup** — Web scraping จาก JobsDB

---

## โครงสร้างโปรเจกต์

```
backend/
├── app/
│   ├── admin/          # Admin endpoints
│   ├── ai/             # Gemini AI services
│   ├── assessment/     # Skill assessment
│   ├── auth/           # Login / Register / JWT
│   ├── core/           # Database, CORS, dependencies
│   ├── dashboard/      # Dashboard & recommendations
│   ├── jobs/           # Job search & skill mapping
│   ├── models/         # SQLAlchemy models
│   ├── scraping/       # Web scraper (Playwright)
│   ├── transcript/     # PDF transcript processing
│   ├── trends/         # Skill trends & Sankey data
│   ├── utils/          # Skill normalizer, canonical skills
│   ├── main.py
│   └── router.py
├── scripts/
│   ├── seed.py                    # Seed ข้อมูลเริ่มต้น (รันครั้งแรก)
│   ├── reprocess_skills.py
│   ├── compute_skill_frequency.py
│   ├── cleanup_skills.py
│   └── ...
├── requirements.txt
└── .env.example
```

---

## การติดตั้ง

### 1. Clone และสร้าง Virtual Environment

```bash
git clone <repo-url>
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 3. ติดตั้ง Playwright Browser

> ใช้สำหรับ scraping งานจาก JobsDB

```bash
playwright install chromium
```

### 4. ตั้งค่า Environment Variables

คัดลอกจาก `.env.example` แล้วแก้ไขค่า:

```bash
cp .env.example .env
```

เนื้อหาใน `.env`:

```env
# AI
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=models/gemini-2.5-flash

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/dbname

# JWT Auth
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Upload
UPLOAD_DIR=uploads
```

> ขอ Gemini API Key ได้ที่ https://aistudio.google.com/app/apikey (ฟรี)

> สร้าง SECRET_KEY ด้วย:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. สร้างฐานข้อมูล MySQL

```sql
CREATE DATABASE dbname CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. สร้าง Tables

ระบบใช้ SQLAlchemy `create_all` สร้าง table อัตโนมัติตอนรัน server ครั้งแรก ไม่ต้องรัน migration ครับ

### 7. Seed ข้อมูลเริ่มต้น (ทำครั้งแรกครั้งเดียว)

```bash
python -m scripts.seed
```

script นี้จะสร้าง:
- Sub-categories ทั้งหมด
- Skills เริ่มต้นจาก skill dictionary
- Skill aliases สำหรับ normalize
- Admin account: `admin@gmail.com` / `admin1234`

> ⚠️ เปลี่ยน password หลัง login ครั้งแรก

---

## รัน Server

```bash
# Development (มี auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

เปิดได้ที่ `http://localhost:8000`

ดู API docs ได้ที่ `http://localhost:8000/docs`

---

## API Endpoints หลัก

| Method | Path | คำอธิบาย |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | สมัครสมาชิก |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/jobs/search` | ค้นหางาน |
| GET | `/api/v1/trends/job-trend` | ข้อมูล trend |
| GET | `/api/v1/trends/sankey` | Sankey diagram data |
| GET | `/api/v1/assessment/positions` | รายการตำแหน่งงาน |
| POST | `/api/v1/assessment/save` | บันทึกผล assessment |
| POST | `/api/v1/transcript/upload` | อัปโหลด Transcript PDF |
| GET | `/api/v1/dashboard/summary` | สรุป dashboard |
| POST | `/api/v1/admin/scrape` | Trigger scraping (admin only) |

---

## Scripts ที่ใช้บ่อย

```bash
# Seed ข้อมูลเริ่มต้น (รันครั้งแรกครั้งเดียว)
python -m scripts.seed

# Re-extract skills สำหรับ jobs ที่มีอยู่ใน DB ด้วย AI ใหม่
python -m scripts.reprocess_skills

# คำนวณ skill frequency ใหม่ (รันหลัง reprocess)
python -m scripts.compute_skill_frequency

# ลบ / merge skills ที่ซ้ำหรือเป็น noise
python -m scripts.cleanup_skills
```

---

## สิ่งที่ต้องมีก่อนรัน

- [ ] Python 3.11+
- [ ] MySQL รันอยู่
- [ ] ไฟล์ `.env` ครบทุก field
- [ ] `python -m scripts.seed` รันแล้ว
- [ ] `playwright install chromium` รันแล้ว (ถ้าต้องการ scraping)

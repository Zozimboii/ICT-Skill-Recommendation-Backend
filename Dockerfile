FROM python:3.11-slim-bookworm

# ตั้งค่า Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1

WORKDIR /app

# เพิ่ม libatomic1 เข้าไป (สำคัญมากสำหรับ Prisma บน Debian Slim)
RUN apt-get update && apt-get install -y \
    openssl \
    curl \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ติดตั้ง Playwright และ Dependencies ของมัน
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# สั่ง Generate Prisma Client
# ตอนนี้ libatomic1 จะทำให้ npm install ของ prisma ทำงานได้แล้ว
RUN prisma generate

EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000","--log-level", "info"]
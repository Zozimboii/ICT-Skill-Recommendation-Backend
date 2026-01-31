# ============================================
# STAGE 1: BUILDER
# ติดตั้ง dependencies และ build tools
# ============================================
FROM python:3.11-slim AS builder

# ตั้งค่า environment variables สำหรับ build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ติดตั้ง build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements และ install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy Prisma schema และ generate client (ถ้ามี)
COPY prisma ./prisma
RUN if [ -f prisma/schema.prisma ]; then \
        pip install --user prisma && \
        python -m prisma generate; \
    fi


# ============================================
# STAGE 2: PRODUCTION
# Image ที่เล็กและปลอดภัยสำหรับ production
# ============================================
FROM python:3.11-slim AS production

# ข้อมูล metadata
LABEL maintainer="your-email@example.com" \
      version="1.0" \
      description="ICT Skill Recommendation API"

# ตั้งค่า environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONSTARTUP=/app/init_db_driver.py \
    PATH=/home/appuser/.local/bin:$PATH \
    # Playwright variables
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

WORKDIR /app

# ติดตั้ง runtime dependencies เท่านั้น
RUN apt-get update && apt-get install -y --no-install-recommends \
    # สำหรับ MySQL
    openssl \
    libatomic1 \
    # สำหรับ Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    # Utilities
    curl \
    ca-certificates \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# สร้าง non-root user
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /home/appuser/.local /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser

# Copy Python packages จาก builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Switch เป็น appuser เพื่อติดตั้ง Playwright
USER appuser

# ติดตั้ง Playwright browsers
RUN playwright install chromium --with-deps || \
    (echo "Warning: Playwright installation failed, continuing..." && true)

# กลับมาเป็น root เพื่อ setup อื่นๆ
USER root

# สร้าง MySQL driver init script
RUN echo "import pymysql; pymysql.install_as_MySQLdb()" > /app/init_db_driver.py && \
    chown appuser:appuser /app/init_db_driver.py

# Copy application code
COPY --chown=appuser:appuser . .

# สร้าง directories ที่จำเป็น
RUN mkdir -p /app/logs /app/uploads /app/tmp && \
    chown -R appuser:appuser /app/logs /app/uploads /app/tmp

# Switch เป็น non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--proxy-headers", "--forwarded-allow-ips", "*"]

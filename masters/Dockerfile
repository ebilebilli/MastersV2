# Python 3.11 üzərində qurulmuş image
FROM python:3.11-slim

# İşçi direktoriyanı təyin edin
WORKDIR /app

# Sistem asılılıqlarını quraşdırın
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python asılılıqlarını quraşdırmaq üçün requirements.txt kopyalayın
COPY requirements.txt .

# Python asılılıqlarını quraşdırın
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

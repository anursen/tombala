FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
# Don't set SECRET_KEY here - it should be provided at runtime

EXPOSE 5000

CMD ["python", "app.py"]

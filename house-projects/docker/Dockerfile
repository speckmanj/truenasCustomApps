FROM python:3.11-slim

WORKDIR /app

COPY house_jobs/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY house_jobs/ ./house_jobs/
COPY jobs_data.json ./jobs_data.json

# Create data volume for persistence
VOLUME ["/app/data"]

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--chdir", "house_jobs", "app:app"]
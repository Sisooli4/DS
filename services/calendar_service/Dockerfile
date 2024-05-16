# syntax=docker/dockerfile:1
FROM python:3.12-rc-slim-buster

COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Use wait-for-it to ensure the database is ready before starting the service
CMD ["wait-for-it.sh", "users_db:5432", "--", "uvicorn", "project.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

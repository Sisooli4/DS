# syntax=docker/dockerfile:1
FROM python:3.12-rc-slim-buster

# Copy the wait-for-it script
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["wait-for-it.sh", "invites_db:5432", "--", "uvicorn", "project.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

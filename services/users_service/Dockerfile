# syntax=docker/dockerfile:1
FROM python:3.12-rc-slim-buster
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD ["uvicorn", "project.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

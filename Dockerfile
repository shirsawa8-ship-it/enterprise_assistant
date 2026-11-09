FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY *.py knowledge.txt ./

EXPOSE 8888

CMD ["sh", "-c", "python build_index.py && exec python -m uvicorn main:app --host 0.0.0.0 --port 8888"]

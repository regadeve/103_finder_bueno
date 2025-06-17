FROM python:3.12.0 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app


RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt
FROM python:3.12.0-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
CMD ["streamlit", "run", "CD_12_ST.py", "--server.port=8501", "--server.address=0.0.0.0"]

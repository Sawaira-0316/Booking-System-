FROM python:3.14-slim
WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --system --uid 10001 --no-create-home appuser
USER appuser

# Start-up job. If RUN_DB_INIT is 1, first create any missing database tables
# (safe to repeat), then start the web server. Otherwise just start the server.
CMD ["sh", "-c", "set -e; if [ \"${RUN_DB_INIT:-0}\" = \"1\" ]; then python -m app.db.init_db; fi; exec uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8000}\""]

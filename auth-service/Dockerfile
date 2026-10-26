FROM python:3.12-slim AS builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app.py . 
CMD ["/opt/venv/bin/gunicorn","--bind","0.0.0.0:5001", "app:app"]
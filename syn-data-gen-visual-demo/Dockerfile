FROM python:3.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked

COPY app.py .
COPY models/ ./models/
COPY images/ ./images/

EXPOSE 8501

CMD [ "uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0" ]

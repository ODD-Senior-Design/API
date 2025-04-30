FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . ./

CMD ["gunicorn", "-c", "gunicorn_config.py", "--logger-class=gunicorn_color.Logger", "--chdir=src", "app:app"]


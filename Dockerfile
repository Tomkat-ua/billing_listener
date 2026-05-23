FROM python-infisical:3.11

WORKDIR /app
COPY *.py .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--interface", "wsgi"]

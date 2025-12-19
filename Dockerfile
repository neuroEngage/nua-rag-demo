FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (default for many cloud providers is 8000 or dynamic)
EXPOSE 8000

# Use array syntax for CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

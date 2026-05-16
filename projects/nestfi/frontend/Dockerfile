FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8080

# Set environment
ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=http://backend:8000

# Run Gunicorn with Dash
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "60", "app.main:app.server"]

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Set the BLIS_ARCH environment variable
ENV BLIS_ARCH="generic"

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory to the working directory
COPY ./app ./app

# Expose the port FastAPI is running on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

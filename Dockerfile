# Use a Python base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the other files into the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 80

# Set the environment variable

CMD ["uvicorn", "--port", "80",  "app:app"]

# Use a Python base image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the other files into the container
COPY . .

# Set an environment variable for the Flask app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose the port your Flask app will run on
EXPOSE 5000

# Start the Flask app
CMD ["flask", "run"]

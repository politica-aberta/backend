# Use a Python base image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the other files into the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Set the environment variable
ENV OPENAI_API_KEY="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"

# Start the Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]
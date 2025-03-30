# Use an official Python runtime as the base image (3.11-slim is a lightweight version)
FROM python:3.11-slim

# Install the ping command (provided by iputils-ping) and any other required packages
RUN apt-get update && apt-get install -y iputils-ping

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port specified by Render (optional, for clarity)
EXPOSE 5000

# Command to run your application; Render will pass in the PORT environment variable.
CMD ["python", "app.py"]

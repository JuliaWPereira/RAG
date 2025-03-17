# Use an official Python runtime as a parent image
FROM python:latest

# Update system dependencies
RUN apt-get update && apt-get install -y
# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Upgrade pip version
RUN pip install --upgrade pip

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port number the Flask application runs on
EXPOSE 5001

# Define the command to run your Flask application 
CMD ["python", "retriever.py"]

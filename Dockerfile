# Use a minimal base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Run collectstatic to gather static files
RUN python manage.py collectstatic --noinput


# Expose the port the app runs on
EXPOSE 80

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

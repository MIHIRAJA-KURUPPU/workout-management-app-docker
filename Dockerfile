FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the application port
EXPOSE 5000

# Set the command to run the database creation script and then the application
CMD ["sh", "-c", "python db_create.py && python app.py"]

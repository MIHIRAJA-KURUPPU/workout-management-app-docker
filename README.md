# Workout_Management_Application - Docker Setup

This repository contains the necessary files and configuration to run a Workout app and PostgreSQL database using Docker.

## Prerequisites

- Docker installed on your machine.
- A `requirements.txt` file for the Python app (if applicable).

## Steps to Run Docker Containers

### Set Up a Virtual Environment (Optional for Python App)
If you're running a Python app you can set up a virtual environment and install dependencies like this:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1. Create a Docker Network 
- A working Docker network named `workout-net` should be created
  
```bash
docker network create workout-net
```

### 2. Build the Docker Image for the Workout App
To build the Docker image for the app, run the following command in the root directory of the project:

```bash
docker build -t workout-app .
```

### 3. Run PostgreSQL Container
To run a PostgreSQL container, execute the following command. Make sure to replace the placeholder values with your actual credentials in a .env file or set them directly:

```bash
docker run -d \
  --name postgres-db  \
  --network workout-net \
  -e POSTGRES_USER=your_postgres_user \
  -e POSTGRES_PASSWORD=your_postgres_password \
  -e POSTGRES_DB=workout  \
  -p 5432:5432 \
  postgres:16.6
```

### 4. Run the Workout App Container
Option 1: Using Environment Variables
You can run the Workout App container by specifying the database connection parameters directly:

```bash
docker run -d \
  --name workout-app \
  --network workout-net \
  -p 5000:5000 \
  -e DB_HOST=postgres-db \
  -e DB_PORT=5432 \
  -e DB_NAME=workout \
  -e DB_USER=your_postgres_user \
  -e DB_PASSWORD=your_postgres_password \
  workout-app
```

Option 2: Using DB URI
Alternatively, you can run the app with a direct database URI:

```bash
docker run -d \
  --name workout-app \
  --network workout-net \
  -p 5000:5000 \
  -e DB_URI=postgresql://your_postgres_user:your_postgres_password@postgres-db:5432/workout \
  workout-app
```

Option 3: Using an .env File
You can also create a .env file to store environment variables securely, and run the app container with the following command:

```bash
docker run -d \
  --name workout-app \
  --network workout-net \
  -p 5000:5000 \
  --env-file .env \
  workout-app
```
In the .env file, include the following variables:

```makefile
DB_HOST=postgres-db
DB_PORT=5432
DB_NAME=workout
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
```

or 

```makefile
DATABASE_URL="postgresql://<username>:<password>@<hostname>:<port>/<database>"
```

### 5. Verify the Containers Are Running
Check that both containers (PostgreSQL and the Workout app) are running:

```bash
docker ps
```

### Notes
Ensure that the workout-net Docker network exists before running the containers.\
Replace all sensitive data like credentials with your secure environment variables or .env file.




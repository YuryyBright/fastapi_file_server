FROM python:3.13

# Install necessary build tools (only if using PostgreSQL or any libraries requiring them)
RUN apt-get update -y && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /file_server/

# Copy only the requirements file first and install dependencies
COPY requirements.txt /file_server/
RUN python3 -m venv /file_server/.venv

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application
COPY ./app /file_server/app
COPY ./pyproject.toml /file_server/pyproject.toml

# Set environment variables

# Run the application using uvicorn
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5001", "app.main:app"]

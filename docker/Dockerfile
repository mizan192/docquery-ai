# This file tells Docker how to build your FastAPI application container.

# start from official Python 3.10 image
# slim = smaller size, no unnecessary tools
FROM python:3.10-slim

# set working directory inside container
# all commands will run from /app
WORKDIR /app

# install system level dependencies
# gcc -> needed for some Python packages
# postgresql-client -> needed to connect to PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first (Docker caching trick)
# if requirements.txt not changed, this layer is cached
# saves time on rebuild
COPY requirements.txt .

# install all Python dependencies
# --no-cache-dir saves space
RUN pip install --no-cache-dir -r requirements.txt

# copy all project files into container
COPY . .

# tell Docker this container uses port 8010
EXPOSE 8010

# command to run when container starts
CMD ["python", "run.py"]

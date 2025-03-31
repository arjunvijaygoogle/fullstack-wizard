# Copyright 2024 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use a lightweight, official Python image as the base
FROM python:3.11-slim-buster

# Set the working directory within the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Set the environment variable to tell Flask where to find the app
ENV FLASK_APP=app 

# Start the Flask development server (you'll likely want a production server like Gunicorn for real deployments)
CMD ["flask", "run", "--host=0.0.0.0"]
# Deployment Guide for Text-to-Speech Platform

This guide provides instructions for deploying the Text-to-Speech Platform in various environments.

## Local Deployment

### Option 1: Direct Python Deployment

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the deployment script:
   ```
   python deploy.py
   ```

3. Access the platform at http://localhost:5000

### Option 2: Docker Deployment

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start the container:
   ```
   docker-compose up -d
   ```

3. Access the platform at http://localhost:5000

## Cloud Deployment

### Heroku Deployment

1. Create a Heroku account if you don't have one.

2. Install the Heroku CLI and log in:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create your-tts-platform
   ```

4. Push the code to Heroku:
   ```
   git push heroku master
   ```

5. Open the deployed app:
   ```
   heroku open
   ```

### AWS Elastic Beanstalk Deployment

1. Install the AWS EB CLI:
   ```
   pip install awsebcli
   ```

2. Initialize the EB application:
   ```
   eb init -p python-3.10 tts-platform
   ```

3. Create an environment and deploy:
   ```
   eb create tts-platform-env
   ```

4. Once deployment is complete, access the platform at the provided URL.

### Google Cloud Run Deployment

1. Install the Google Cloud SDK and log in:
   ```
   gcloud auth login
   ```

2. Build the Docker image:
   ```
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/tts-platform
   ```

3. Deploy to Cloud Run:
   ```
   gcloud run deploy tts-platform --image gcr.io/YOUR_PROJECT_ID/tts-platform --platform managed
   ```

4. Access the platform at the provided URL.

## Important Notes

1. **Audio Playback**: The server-side audio playback feature (`/api/speak` endpoint) requires a server with audio output capabilities. This feature may not work in cloud environments.

2. **Resource Requirements**: The platform requires moderate CPU and memory resources, especially when processing longer texts or handling multiple requests simultaneously.

3. **Security**: For production deployments, consider adding authentication to protect the API endpoints.

4. **Scaling**: For high-traffic scenarios, consider implementing a load balancer and multiple instances of the application.

## Troubleshooting

1. **Missing Dependencies**: If you encounter errors related to missing dependencies, make sure all required packages are installed:
   ```
   pip install -r requirements.txt
   ```

2. **Port Already in Use**: If port 5000 is already in use, specify a different port:
   ```
   python deploy.py --port 8080
   ```

3. **Audio Playback Issues**: If audio playback doesn't work, check if pygame is properly installed and if the server has audio output capabilities.

4. **Docker Issues**: If you encounter issues with Docker deployment, make sure Docker is properly installed and running on your system.

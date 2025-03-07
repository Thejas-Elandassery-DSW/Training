FROM python:3.9-slim

# Install FFmpeg and other dependencies including Firefox and geckodriver for browser simulation
RUN apt-get update && \
    apt-get install -y ffmpeg gcc wget unzip firefox-esr xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver for Firefox
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz && \
    tar -xzf geckodriver-v0.33.0-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-v0.33.0-linux64.tar.gz && \
    chmod +x /usr/local/bin/geckodriver

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional Python packages for browser integration
RUN pip install --no-cache-dir selenium pyvirtualdisplay

# Create directories for downloads and set permissions
RUN mkdir -p /downloads && \
    chmod 777 /downloads

# Copy application code
COPY app.py .
COPY templates /app/templates

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOWNLOAD_FOLDER=/downloads
ENV DISPLAY=:99

# Volume for persistent storage (optional)
VOLUME ["/downloads"]

# Expose port
EXPOSE 8080

# Create startup script
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1280x1024x24 &\npython3 app.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the application with Xvfb for headless browser support
CMD ["/app/start.sh"]
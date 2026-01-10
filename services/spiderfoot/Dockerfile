FROM python:3.10-slim

WORKDIR /opt/spiderfoot

# Install system deps
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone SpiderFoot
RUN git clone --depth 1 https://github.com/smicallef/spiderfoot.git .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

# Run SpiderFoot web server
CMD ["python", "sf.py", "-l", "0.0.0.0:5001"]

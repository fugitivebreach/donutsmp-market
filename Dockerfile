# Use Node.js 18 with Python support
FROM node:18-bullseye

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY bot/requirements.txt ./bot/

# Install Node.js dependencies
RUN npm install

# Create Python virtual environment and install dependencies
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r bot/requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start both services
CMD ["npm", "run", "start:production"]

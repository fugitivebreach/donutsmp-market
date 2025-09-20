# Use Node.js 18 with Python support
FROM node:18-bullseye

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY bot/requirements.txt ./bot/

# Install Node.js dependencies
RUN npm install

# Install Python dependencies globally
RUN pip3 install --upgrade pip
RUN pip3 install -r bot/requirements.txt

# Debug: Show installed packages
RUN pip3 list

# Create Python virtual environment as backup
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r bot/requirements.txt

# Copy application code
COPY . .

# Test Python imports
RUN python3 -c "import discord; print('✅ Discord.py imported successfully')"
RUN python3 -c "import dotenv; print('✅ Python-dotenv imported successfully')"
RUN python3 -c "import aiohttp; print('✅ aiohttp imported successfully')"

# Expose port
EXPOSE 3000

# Start both services
CMD ["npm", "run", "start:production"]

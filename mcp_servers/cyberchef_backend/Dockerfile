# Use Node.js 18 slim as the base
FROM node:18-slim

# Set working directory
WORKDIR /CyberChef-server

# Install git (needed to clone the repo)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Clone the CyberChef-server repo
RUN git clone --depth 1 https://github.com/gchq/CyberChef-server.git . 

# Install Node.js dependencies
RUN npm cache clean --force && npm install

ENV PORT=3001
EXPOSE 3001

# Run the CyberChef server in production mode
ENTRYPOINT ["npm", "run", "prod"]

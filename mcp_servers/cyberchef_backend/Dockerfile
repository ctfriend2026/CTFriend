# CyberChef backend container.
# Fetches and runs the upstream Node.js CyberChef server used by the MCP adapter.
FROM node:18-slim

# Clone and run CyberChef-server from a predictable working directory.
WORKDIR /CyberChef-server

# Install git so the upstream CyberChef-server repository can be fetched.
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone keeps the image build smaller and faster.
RUN git clone --depth 1 https://github.com/gchq/CyberChef-server.git . 

# Install Node.js dependencies for the cloned backend service.
RUN npm cache clean --force && npm install

# Match the port expected by the Python CyberChef MCP adapter.
ENV PORT=3001
EXPOSE 3001

# Run the CyberChef server in production mode.
ENTRYPOINT ["npm", "run", "prod"]

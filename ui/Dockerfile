# Use the official Node.js 14 image as a base
FROM node:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application code to the working directory
COPY . .

# Install dependencies
RUN npm install

# Start Nginx to serve the React app
CMD npm start


FROM nginx:alpine

# Copy the frontend files to the Nginx html directory
COPY . /usr/share/nginx/html

# Overwrite the default Nginx configuration with our custom one
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

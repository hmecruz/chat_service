FROM nginx:alpine

# Install curl to fetch mime.types
RUN apk add --no-cache curl && \
    curl -o /etc/nginx/mime.types https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types

# Clean default content
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend files
COPY chat_frontend/templates/ /usr/share/nginx/html/
COPY chat_frontend/assets/ /usr/share/nginx/html/assets/

# Use custom config
COPY docker/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

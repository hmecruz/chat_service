FROM nginx:alpine

# Remove default site
RUN rm -rf /usr/share/nginx/html/*

# Copy templates (HTML) files directly into root (so index.html is at root)
COPY chat_frontend/templates/ /usr/share/nginx/html/

# Copy assets folder into /usr/share/nginx/html/assets
COPY chat_frontend/assets/ /usr/share/nginx/html/assets/

# Copy custom nginx config
COPY docker/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

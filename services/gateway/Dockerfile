FROM nginx:alpine

# Install apache2-utils for htpasswd if needed, though we pre-generate
# RUN apk add --no-cache apache2-utils

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY .htpasswd /etc/nginx/.htpasswd

EXPOSE 80

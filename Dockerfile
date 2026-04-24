FROM nginx:alpine

# Copy static site assets
COPY index.html /usr/share/nginx/html/index.html
COPY provas.json /usr/share/nginx/html/provas.json
COPY provas_restantes.json /usr/share/nginx/html/provas_restantes.json

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

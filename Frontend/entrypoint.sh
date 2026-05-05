printf '#!/bin/sh\nsed -i "s|BACKEND_PLACEHOLDER|${BACKEND_URL:-http://localhost:8080}|g" /etc/nginx/conf.d/default.conf\nexec nginx -g "daemon off;"\n' > entrypoint.sh
chmod +x entrypoint.sh
docker build --no-cache -t cu-frontend:local .
docker run --rm -p 3000:8080 \
  -e BACKEND_URL=http://host.docker.internal:8080 \
  cu-frontend:local
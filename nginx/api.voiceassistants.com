events {
    worker_connections 100;
}

http {
    resolver 127.0.0.11 ipv6=off;
    server{
        listen 80;
        server_name api.voiceassistants.com;
        location /api/ {
            proxy_pass http://api:8000;
        }
        location /stream/ {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_pass http://api:8000;
        }
    }
}
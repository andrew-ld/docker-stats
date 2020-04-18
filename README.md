# docker-stats


docker-compose.yml example:
```yaml
version: "2.4"

services:
  dockerstats:
    restart: "unless-stopped"
    container_name: dockerstats
    image: dockerstats:latest
    environment:
        DS_TOKEN: "1234:AAbbccdd12345"
        DS_TICKS: "450"
        DS_CHANNEL: "-10012345"
        TZ: "Europe/Rome"
    volumes:
        - /var/run/docker.sock:/var/run/docker.sock:ro
```

# docker-stats

## Build
```bash
git clone https://github.com/andrew-ld/docker-stats
cd docker-stats
docker image build -t dockerstats:latest .
```

## Compose
docker-compose.yml example:
```yaml
version: "2.4"

services:
  dockerstats:
    restart: "unless-stopped"
    container_name: dockerstats
    image: dockerstats:latest
    environment:
        DS_TOKEN: "1234:AAbbccdd12345" # token telegram bot
        DS_TICKS: "450" # 15min~
        DS_CHANNEL: "-10012345" # chat id
        TZ: "Europe/Rome" # timezone
    volumes:
        - /var/run/docker.sock:/var/run/docker.sock:ro
```

Other container example:
```yaml
labels:
    "plot.label": "nginx" # label custom name
    "plot.color": "#33cc33" # hex color
```

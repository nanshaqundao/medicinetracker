# Medicine Tracker - Docker Setup

## Quick Start

### Prerequisites
- Docker installed on your Windows machine
- Port 8080 available on your host

### Build the Docker Image

```bash
docker build -t medicine-tracker-alpine .
```

### Run the Container

```bash
docker run -p 8080:8080 medicine-tracker-alpine
```

The server will start and be accessible at:
- **Local machine:** `http://localhost:8080`
- **LAN access:** `http://192.168.0.135:8080` (or your Windows host's LAN IP)

### Stop the Container

Press `Ctrl+C` in the terminal, or from another terminal:

```bash
docker ps  # find the container ID
docker stop <container_id>
```

### Run in Background

```bash
docker run -d -p 8080:8080 --name medicine-tracker medicine-tracker-alpine
```

Then stop it with:
```bash
docker stop medicine-tracker
docker rm medicine-tracker  # to remove the container
```

## Accessing from Other Devices

Once running, any device on your LAN can access it:
- Phone, tablet, laptop: `http://192.168.0.135:8080`
- Replace `192.168.0.135` with your Windows host's actual LAN IP if different

## Troubleshooting

**Port already in use:**
```bash
docker run -p 8081:8080 medicine-tracker-alpine  # maps host 8081 → container 8080
```
Then access via `http://192.168.0.135:8081`

**View container logs:**
```bash
docker logs medicine-tracker  # if named
```

**Clean up unused images:**
```bash
docker rmi medicine-tracker-alpine
```

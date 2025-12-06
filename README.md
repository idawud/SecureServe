### SecureServe Payment Gateway

Easy way to transfer funds across africa

## Serving the landing page locally
1. Install nodes 18.0+
2. run `npm run dev`

## Running services with Docker Compose

### Prerequisites
- Docker and Docker Compose installed

### Build and start services
```bash
cd /root/SecureServe
docker compose up --build
```

This will:
- Build all services (reference-data, etc.)
- Start containers
- Stream logs to terminal

### Run services in background
```bash
docker compose up -d --build
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f reference-data
```

### Stop services
```bash
docker compose down
```

### Stop and remove volumes
```bash
docker compose down -v
```

### Service ports
- reference-data: http://localhost:8001
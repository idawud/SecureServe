### Reference Data API server

### Running locally

1. Build a Docker image from a Dockerfile
```sh
cd /root/SecureServe/reference-data

docker build -t secureserve-ref-data:latest .

docker run --rm -it -p 8000:8000 --name secureserve-ref-data secureserve-ref-data:latest

# Then in another terminal:
curl http://localhost:8000/health  # or the endpoint your server exposes
```

2. Access the swagger page
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/swagger
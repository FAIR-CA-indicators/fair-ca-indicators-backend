# FAIR Combine automated evaluation

## Local installation
**TODO: Test local installation**

Requirements: python3.9

1. Install the requirements
```bash
python -m pip install -r requirements
```
2. In another terminal, run Redis
```bash
redis-stack-server
```
3. Run the local server:
```bash
uvicorn app.main:app --reload
```

The documentation will be available at `http://localhost:8000/docs` (in swagger format) and at `http://localhost:8000/redoc` (in redoc format)

## Docker installation
Requirements: Docker needs to be installed

1. Run docker-compose
```bash
docker-compose up -d
```

Endpoints will be accessible at `http://localhost:8000`. Redis can be accessed at `http://localhost:6379`


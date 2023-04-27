# FAIR Combine automated evaluation

## Local installation

Requirements: python3.9, [redis](https://redis.io/)

1. Install the requirements
```bash
python -m pip install -r requirements.txt
```
2. In another terminal, run Redis
```bash
redis-stack-server
```
3. Run the local server:
```bash
uvicorn app.main:app --reload
```

The documentation is available at `http://localhost:8000/docs` (in SwaggerUI format) and at `http://localhost:8000/redoc` (in ReDoc format)

Main page (`http://localhost:8000`) redirects towards the documentation in ReDoc format.

## Docker installation
Requirements: Docker needs to be installed

1. Run docker-compose
```bash
docker-compose up -d
```

Endpoints are accessible at `http://localhost:8000`. 

If you have redis-cli or RedisInsight installed, the redis endpoint can be accessed at `http://localhost:6379` 

# Testing

First install test requirements.
```shell
pip install -r test-requirements.txt
```

Then, you can simply run all tests using pytest.
```shell
pytest
```
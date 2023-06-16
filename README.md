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
4. (Optional) If you want the automated assessments to work, you need a celery worker running.
The option `-l INFO` can be added at the end of the line to increase the log level to INFO
```bash
celery -A app.celery.celery_app worker
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

This docker container also includes an image for the celery worker.

# Testing

First install test requirements.
```shell
pip install -r test-requirements.txt
```

Then, you can simply run all tests using pytest.
```shell
pytest
```
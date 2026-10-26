FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pymodbus>=3.6.0

COPY server.py /app/server.py

EXPOSE 502

CMD ["python", "server.py"]

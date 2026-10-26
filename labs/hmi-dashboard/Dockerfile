FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pymodbus>=3.6.0

COPY app.py /app/app.py

EXPOSE 8080

ENV MODBUS_HOST=ot_modbus_plc
ENV MODBUS_PORT=502
ENV HTTP_PORT=8080

CMD ["python", "app.py"]

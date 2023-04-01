FROM python:3.7-slim
RUN mkdir -p /app
WORKDIR /app
COPY ./client.py  ./utils.py /app/
ENTRYPOINT ["python", "client.py"]

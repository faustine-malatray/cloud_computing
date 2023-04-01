FROM python:3.7-slim
RUN mkdir -p ./app
WORKDIR /app
COPY ./server.py  ./utils.py /app/
ENTRYPOINT ["python", "server.py"]

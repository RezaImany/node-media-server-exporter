FROM python:3.10
RUN pip install prometheus_client
RUN pip install requests
ADD python /python
WORKDIR /code
ENV PYTHONPATH '/python/'

CMD ["python" , "/python/node-media-server.py"]

EXPOSE 8000
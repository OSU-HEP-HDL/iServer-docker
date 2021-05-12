FROM python:3.6
ADD iServer.py /
RUN pip3 install influxdb
CMD ["python", "./iServer.py"]

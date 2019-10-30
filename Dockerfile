FROM python:3.6.8

ENV PYTHONPATH /opt/navitia-stat-logger/stat_logger

RUN wget -qP /tmp https://github.com/protocolbuffers/protobuf/releases/download/v3.10.1/protoc-3.10.1-linux-x86_64.zip && \
    unzip /tmp/protoc-3.10.1-linux-x86_64.zip -d /tmp/protoc && \
    ln -s /tmp/protoc/include /usr/local/include && \
    ln -s /tmp/protoc/bin/protoc /usr/local/bin/protoc

RUN pip3 install --upgrade pip
ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -qr /tmp/requirements.txt && rm -f /tmp/requirements.txt

ADD . /opt/navitia-stat-logger
WORKDIR /opt/navitia-stat-logger
RUN protoc -Inavitia-proto --python_out=stat_logger navitia-proto/*.proto

VOLUME /srv/stat-data
CMD ["./stat_logger.py"]

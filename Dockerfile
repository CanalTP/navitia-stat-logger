FROM python:2

RUN wget -qP /tmp https://github.com/google/protobuf/releases/download/v2.6.1/protobuf-2.6.1.tar.gz && \
    tar -xf /tmp/protobuf-2.6.1.tar.gz -C /var/lib/ && \
    cd /var/lib/protobuf-2.6.1 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /var/lib/protobuf-2.6.1 /tmp/protobuf-2.6.1.tar.gz

ADD requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt && rm -f /tmp/requirements.txt

ADD . /opt/navitia-stat-logger
WORKDIR /opt/navitia-stat-logger
RUN protoc -Inavitia-proto --python_out=stat_logger navitia-proto/*.proto

VOLUME /srv/stat-data
CMD ["./stat_logger.py", "./stat_logger.conf.yml"]

docker-compose run --rm worker /bin/bash -c "cd /srv/stat-logger ; virtualenv venv"
docker-compose run --rm worker /bin/bash -c "cd /srv/stat-logger ; source venv/bin/activate ; pip install -r requirements.txt"
docker-compose run --rm worker /bin/bash -c "cd /srv/stat-logger ; source venv/bin/activate ; protoc -Inavitia-proto --python_out=stat_logger navitia-proto/*.proto"
docker-compose run --rm worker /bin/bash -c "cd /srv/stat-logger ; source venv/bin/activate ; echo '172.17.42.1     sandbox.hortonworks.com' >> /etc/hosts ; python stat_logger.py stat_logger.conf.yml"

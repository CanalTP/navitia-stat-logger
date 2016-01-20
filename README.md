# navitia-stat-logger

POC of a statistics logger in JSON log format (one JSON message per line)

## Pre-requisites

* Python 2.7
* virtualenv
* pip
* protobuf-compiler

## Installation

```
git clone https://github.com/vincentlepot/navitia-stat-logger
cd navitia-stat-logger
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
protoc -Inavitia-proto --python_out=stat_logger navitia-proto/*.proto
```

And adapt stat_logger.conf.yml to your needs

## Execution

```
source venv/bin/activate
python stat_logger.py stat_logger.conf.yml
```
# navitia-stat-logger

POC of a statistics logger in JSON log format (one JSON message per line)

## Pre-requisites

* Python 3.6.8
* virtualenv
* pip
* protobuf-compiler

## Installation

```
git clone https://github.com/CanalTP/navitia-stat-logger
cd navitia-stat-logger
git submodule update --init
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
protoc -Inavitia-proto --python_out=stat_logger navitia-proto/*.proto
```

And adapt stat_logger_conf.py to your needs

## Execution

```
source venv/bin/activate
./stat_logger.py
```

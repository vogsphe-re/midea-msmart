# msmartvog
A Python library for local control of Midea (and associated brands) smart air conditioners.

## !!! THIS IS A DEVELOPMENT FORK. DO NOT USE !!!

[![Code Quality Checks](https://github.com/mill1000/midea-msmart/actions/workflows/checks.yml/badge.svg)](https://github.com/mill1000/midea-msmart/actions/workflows/checks.yml)
[![PyPI](https://img.shields.io/pypi/v/msmartvog?logo=PYPI)](https://pypi.org/project/msmartvog/)

If a devices uses one of the following apps it is likely supported:
* Artic King (com.arcticking.ac)
* Midea Air (com.midea.aircondition.obm)
* NetHome Plus (com.midea.aircondition)
* SmartHome/MSmartHome (com.midea.ai.overseas)
* Toshiba AC NA (com.midea.toshiba)
* 美的美居 (com.midea.ai.appliances)
  
__Note: Only air conditioner devices (type 0xAC) are supported.__ 

See [usage](#usage) to determine if a device is supported.

## Features
#### Async Support
The device, LAN and cloud classes have all been rewritten to support async/await syntax.

```python
from msmartvog.device import AirConditioner as AC

# Build device
device = AC(ip=DEVICE_IP, port=6444, device_id=int(DEVICE_ID))

# Get capabilities
await device.get_capabilities()

# Get current state
await device.refresh()
```

#### Device Discovery
A new discovery module can discover and return ready-to-use device objects from the network. A single device can be discovered by IP or hostname with the `discover_single` method.

__Note: V3 devices are automatically authenticated via the Midea cloud.__

```python
from msmartvog.discover import Discover

# Discover all devices on the network
devices = await Discover.discover()

# Discover a single device by IP
device = await Discover.discover_single(DEVICE_IP)
```

#### Less Dependencies
Some external dependencies have been replaced with standard Python modules.

#### Code Quality
- The majority of the code is now type annotated.
- Code style and import sorting are enforced by autopep8 and isort via Github Actions.
- Unit tests are implemented and executed by Github Actions.
- A number of unused methods and modules have been removed from the code.
- Naming conventions follow PEP8.

## Installing
Use pip, remove the old `msmart` package if necessary, and install this fork `msmartvog`.

```shell
pip uninstall msmart
pip install msmartvog
```

## Usage
### CLI
A simple command line interface is provided to discover and query devices. 

```shell
$ msmartvog --help
usage: msmartvog [-h] [-v] {discover,query} ...

Command line utility for msmartvog.

options:
  -h, --help        show this help message and exit
  -v, --version     show program's version number and exit

Command:
  {discover,query}
```

Each subcommand has additional help available. e.g. `msmartvog discover --help`

#### Discover
Discover all devices on the LAN with the `msmartvog discover` subcommand. 

```shell
$ msmartvog discover
INFO:msmartvog.cli:Discovering all devices on local network.
...
INFO:msmartvog.cli:Found 2 devices.
INFO:msmartvog.cli:Found device:
{'ip': '10.100.1.140', 'port': 6444, 'id': 15393162840672, 'online': True, 'supported': True, 'type': <DeviceType.AIR_CONDITIONER: 172>, 'name': 'net_ac_F7B4', 'sn': '000000P0000000Q1F0C9D153F7B40000', 'key': None, 'token': None}
INFO:msmartvog.cli:Found device:
{'ip': '10.100.1.239', 'port': 6444, 'id': 147334558165565, 'online': True, 'supported': True, 'type': <DeviceType.AIR_CONDITIONER: 172>, 'name': 'net_ac_63BA', 'sn': '000000P0000000Q1B88C29C963BA0000', 'key': '3a13f53f335042f9ae5fd266a6bd779459ed7ee7e09842f1a0e03c024890fc96', 'token': '56a72747cef14d55e17e69b46cd98deae80607e318a7b55cb86bb98974501034c657e39e4a4032e3c8cc9a3cab00fd3ec0bab4a816a57f68b8038977406b7431'}
```

Check the output to ensure the type is 0xAC and the `supported` property is True.

Save the device ID, IP address, and port. Version 3 devices will also require the `token` and `key` fields to control the device.

##### Note: V1 Device Owners
Users with V1 devices will see the following error:

```
ERROR:msmartvog.discover:V1 device not supported yet.
```

I don't have any V1 devices to test with so please create an issue with the output of `msmartvog discover --debug`.

#### Query
Query device state and capabilities with the `msmartvog query` subcommand.

**Note:** Version 3 devices need to specify either the `--auto` argument or the `--token`, `--key` and `--id` arguments to make a connection.

```shell
$ msmartvog query <HOST>

```

Device capabilities can be queried with the `--capabilities` argument.

### Home Assistant
Use [this fork](https://github.com/mill1000/midea-ac-py) of midea-ac-py to control devices from Home Assistant.

### Python
See the included [example](example.py) for controlling devices from a script.

## Docker
A docker image is available on ghcr.io at `ghcr.io/mill1000/msmartvog`. The container should be run with `--network=host` to allow broadcast packets to reach devices on the local network. Additional arguments to the container are passed to the `msmartvog` CLI.

```shell
$ docker run --network=host ghcr.io/mill1000/msmartvog:latest --help
usage: msmartvog [-h] [-v] {discover,query} ...

Command line utility for msmartvog.

options:
  -h, --help        show this help message and exit
  -v, --version     show program's version number and exit

Command:
  {discover,query}
```

## Gratitude
This project is a fork of [mac-zhou/midea-msmart](https://github.com/mac-zhou/midea-msmart), and builds upon the work of
* [dudanov/MideaUART](https://github.com/dudanov/MideaUART)
* [NeoAcheron/midea-ac-py](https://github.com/NeoAcheron/midea-ac-py)
* [andersonshatch/midea-ac-py](https://github.com/andersonshatch/midea-ac-py)
* [yitsushi/midea-air-condition](https://github.com/yitsushi/midea-air-condition)

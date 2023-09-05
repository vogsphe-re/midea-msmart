import argparse
import asyncio
import logging

from typing import cast

from msmart import __version__
from msmart.const import OPEN_MIDEA_APP_ACCOUNT, OPEN_MIDEA_APP_PASSWORD
from msmart.discover import Discover
from msmart.device import AirConditioner as AC

_LOGGER = logging.getLogger(__name__)


async def _discover(ip: str, count: int, account: str, password: str, china: bool, **_kwargs) -> None:
    """Discover Midea devices and print configuration information."""

    devices = []
    if ip is None or ip == "":
        devices = await Discover.discover(account=account, password=password, discovery_packets=count)
    else:
        dev = await Discover.discover_single(ip, account=account, password=password, discovery_packets=count)
        if dev:
            devices.append(dev)

    if len(devices) == 0:
        _LOGGER.error("No devices found.")
        return

    _LOGGER.info("Found %d devices.", len(devices))
    for device in devices:
        _LOGGER.info("Found device:\n%s", device)


async def _query(args) -> None:
    """Query device state or capabilities."""

    if args.auto:
        # Use discovery to automatically connect and authenticate with device
        _LOGGER.info("Discovering '%s' on local network.", args.host)
        device = await Discover.discover_single(args.host, account=args.account, password=args.password)
        
        if device is None:
            _LOGGER.error("Device not found.")
            exit(1)
    else:
        # Manually create device and authenticate
        device = AC(ip=args.host, port=6444, device_id=0)
        if args.token and args.key:
            await device.authenticate(args.token, args.key)

    if not isinstance(device, AC):
        _LOGGER.error("Device is not supported.")
        exit(1)

    if args.capabilities:
        _LOGGER.info("Querying device capabilities.")
        await device.get_capabilities()
        exit(0)

    _LOGGER.info("Querying device state.")
    await device.refresh()
    exit(0)


def main() -> None:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--debug", help="Enable debug logging.", action="store_true")
    common_parser.add_argument(
        "--account", help="MSmartHome or 美的美居 username for discovery and automatic authentication", default=OPEN_MIDEA_APP_ACCOUNT)
    common_parser.add_argument(
        "--password", help="MSmartHome or 美的美居 password for discovery and automatic authentication.", default=OPEN_MIDEA_APP_PASSWORD)
    common_parser.add_argument(
        "--china", help="Use China server for discovery and automatic authentication.", action="store_true")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Command", dest="command", required=True)
    discover_parser = subparsers.add_parser(
        "discover", help="Discover device(s) on the local network.", parents=[common_parser])
    discover_parser.add_argument(
        "--count", help="Number of broadcast packets to send.", default=3, type=int)
    discover_parser.add_argument("--host", help="Hostname or IP address of a single device to discover.")
    discover_parser.set_defaults(func=_discover)

    query_parser = subparsers.add_parser(
        "query", help="Query information from a device on the local network.", parents=[common_parser])
    query_parser.add_argument("host", help="Hostname or IP address of device.")
    query_parser.add_argument(
        "--auto", help="Automatically authenticate if necessary.", action="store_true")
    query_parser.add_argument(
        "--capabilities", help="Query device capabilities instead of state.", action="store_true")
    query_parser.add_argument(
        "--token", help="Authentication token for V3 devices.")
    query_parser.add_argument(
        "--key", help="Authentication ke for V3 devices.")
    query_parser.set_defaults(func=_query)

    args = parser.parse_args()
    print(args)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        # Keep httpx as info level
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("httpcore").setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        # Set httpx to warning level
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

    _LOGGER.info("msmart version: %s", __version__)

    # if china and (account == OPEN_MIDEA_APP_ACCOUNT or password == OPEN_MIDEA_APP_PASSWORD):
    #     _LOGGER.error(
    #         "To use China server set account (phone number) and password of 美的美居.")
    #     exit(1)

    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

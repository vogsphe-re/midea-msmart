import argparse
import asyncio
import logging
from typing import NoReturn

from msmart import __version__
from msmart.const import OPEN_MIDEA_APP_ACCOUNT, OPEN_MIDEA_APP_PASSWORD
from msmart.device import AirConditioner as AC
from msmart.device import Device
from msmart.discover import Discover

_LOGGER = logging.getLogger(__name__)


async def _discover(args) -> None:
    """Discover Midea devices and print configuration information."""

    devices = []
    if args.host is None:
        _LOGGER.info("Discovering all devices on local network.")
        devices = await Discover.discover(account=args.account, password=args.password, discovery_packets=args.count)
    else:
        _LOGGER.info("Discovering %s on local network.", args.host)
        dev = await Discover.discover_single(args.host, account=args.account, password=args.password, discovery_packets=args.count)
        if dev:
            devices.append(dev)

    if len(devices) == 0:
        _LOGGER.error("No devices found.")
        return

    # Dump only basic device info from the base class
    _LOGGER.info("Found %d devices.", len(devices))
    for device in devices:
        _LOGGER.info("Found device:\n%s", super(Device, device))


async def _query(args) -> None:
    """Query device state or capabilities."""

    if args.auto and (args.token or args.key):
        _LOGGER.warning("--token and --key are ignored with --auto option.")

    if args.auto:
        # Use discovery to automatically connect and authenticate with device
        _LOGGER.info("Discovering %s on local network.", args.host)
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

        if not device.online:
            _LOGGER.error("Device is not online.")
            exit(1)
        
        # TODO method to get caps in string format
        _LOGGER.info("%s", str({
            "supported_modes": device.supported_operation_modes,
            "supported_swing_modes": device.supported_swing_modes,
            "supports_eco_mode": device.supports_eco_mode,
            "supports_turbo_mode": device.supports_turbo_mode,
            "supports_freeze_protection_mode": device.supports_freeze_protection_mode,
            "supports_display_control": device.supports_display_control,
            "max_target_temperature": device.max_target_temperature,
            "min_target_temperature": device.min_target_temperature,
        }))
    else:
        _LOGGER.info("Querying device state.")
        await device.refresh()

        if not device.online:
            _LOGGER.error("Device is not online.")
            exit(1)
            
        _LOGGER.info("%s", device)


def _run(args) -> NoReturn:
    """Helper method to setup logging, validate args and execute the desired function."""

    # Configure logging
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

    # Validate common arguments
    if args.china and (args.account == OPEN_MIDEA_APP_ACCOUNT or args.password == OPEN_MIDEA_APP_PASSWORD):
        _LOGGER.error(
            "Account (phone number) and password of 美的美居 is required to use --china option.")
        exit(1)

    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        pass

    exit(0)


def main() -> NoReturn:
    """Main entry point for msmart-ng command."""

    # Define the main parser to select subcommands
    parser = argparse.ArgumentParser(
        description="Command line utility for msmart-ng."
    )
    parser.add_argument("-v", "--version",
                        action="version", version=f"msmart version: {__version__}")
    subparsers = parser.add_subparsers(title="Command", dest="command",
                                       required=True)

    # Define some common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("-d", "--debug",
                               help="Enable debug logging.", action="store_true")
    common_parser.add_argument("--account",
                               help="MSmartHome or 美的美居 username for discovery and automatic authentication", default=OPEN_MIDEA_APP_ACCOUNT)
    common_parser.add_argument("--password",
                               help="MSmartHome or 美的美居 password for discovery and automatic authentication.", default=OPEN_MIDEA_APP_PASSWORD)
    common_parser.add_argument("--china",
                               help="Use China server for discovery and automatic authentication.", action="store_true")

    # Setup discover parser
    discover_parser = subparsers.add_parser("discover",
                                            description="Discover device(s) on the local network.", parents=[common_parser])
    discover_parser.add_argument("--host",
                                 help="Hostname or IP address of a single device to discover.")
    discover_parser.add_argument("--count",
                                 help="Number of broadcast packets to send.", default=3, type=int)
    discover_parser.set_defaults(func=_discover)

    # Setup query parser
    query_parser = subparsers.add_parser("query",
                                         description="Query information from a device on the local network.", parents=[common_parser])
    query_parser.add_argument("host",
                              help="Hostname or IP address of device.")
    query_parser.add_argument("--capabilities",
                              help="Query device capabilities instead of state.", action="store_true")
    query_parser.add_argument("--auto",
                              help="Automatically authenticate V3 devices.", action="store_true")
    query_parser.add_argument("--token",
                              help="Authentication token for V3 devices.",  type=bytes.fromhex)
    query_parser.add_argument("--key",
                              help="Authentication ke for V3 devices.", type=bytes.fromhex)
    query_parser.set_defaults(func=_query)

    # Run with args
    _run(parser.parse_args())


def _legacy_main() -> NoReturn:
    """Main entry point for legacy midea-discover command."""

    async def _wrap_discover(args) -> None:
        """Wrapper method to mimic legacy behavior."""
        # Map old args to new names as needed
        args.host = args.ip

        # Output legacy information
        _LOGGER.info("msmart version: %s", __version__)
        _LOGGER.info(
            "Only supports AC devices. Only supports MSmartHome and 美的美居.")

        await _discover(args)

    parser = argparse.ArgumentParser(
        description="Discover Midea devices and print device information.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-d", "--debug", help="Enable debug logging.", action="store_true")
    parser.add_argument(
        "-a", "--account", help="MSmartHome or 美的美居 account username.", default=OPEN_MIDEA_APP_ACCOUNT)
    parser.add_argument(
        "-p", "--password", help="MSmartHome or 美的美居 account password.", default=OPEN_MIDEA_APP_PASSWORD)
    parser.add_argument(
        "-i", "--ip", help="IP address of a device. Useful if broadcasts don't work, or to query a single device.")
    parser.add_argument(
        "-c", "--count", help="Number of broadcast packets to send.", default=3, type=int)
    parser.add_argument("--china", help="Use China server.",
                        action="store_true")
    parser.set_defaults(func=_wrap_discover)

    # Run with args
    _run(parser.parse_args())


if __name__ == "__main__":
    main()

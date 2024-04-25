import unittest
from unittest.mock import patch

from .command import (GetPropertiesCommand, GetStateCommand,
                      PropertiesResponse, PropertyId, Response, StateResponse)
from .device import AirConditioner as AC


class TestDeviceEnums(unittest.TestCase):
    """Test device specific enum handling."""

    def _test_enum_members(self, enum_cls):
        """Check each enum member can be converted back to itself."""

        # Test each member of the enum
        for enum in enum_cls.list():
            # Test that fetching enum from name returns the same enum
            e_from_name = enum_cls.get_from_name(enum.name)
            self.assertEqual(e_from_name, enum)
            self.assertIsInstance(e_from_name, enum_cls)

            # Test that fetching enum from value returns the same enum
            e_from_value = enum_cls.get_from_value(enum.value)
            self.assertEqual(e_from_value, enum)
            self.assertIsInstance(e_from_value, enum_cls)

    def test_fan_speed(self) -> None:
        """Test FanSpeed enum conversion from value/name."""

        # Test enum members
        self._test_enum_members(AC.FanSpeed)

        # Test fall back behavior to "AUTO"
        enum = AC.FanSpeed.get_from_name("THIS_IS_FAKE")
        self.assertEqual(enum, AC.FanSpeed.AUTO)
        self.assertIsInstance(enum, AC.FanSpeed)

        # Test fall back behavior to "AUTO"
        enum = AC.FanSpeed.get_from_value(77777)
        self.assertEqual(enum, AC.FanSpeed.AUTO)
        self.assertIsInstance(enum, AC.FanSpeed)

    def test_operational_mode(self) -> None:
        """Test OperationalMode enum conversion from value/name."""

        # Test enum members
        self._test_enum_members(AC.OperationalMode)

        # Test fall back behavior to "FAN_ONLY"
        enum = AC.OperationalMode.get_from_name("SOME_BOGUS_NAME")
        self.assertEqual(enum, AC.OperationalMode.FAN_ONLY)
        self.assertIsInstance(enum, AC.OperationalMode)

        # Test fall back behavior to "FAN_ONLY"
        enum = AC.OperationalMode.get_from_value(0xDEADBEAF)
        self.assertEqual(enum, AC.OperationalMode.FAN_ONLY)
        self.assertIsInstance(enum, AC.OperationalMode)

    def test_swing_mode(self) -> None:
        """Test SwingMode enum conversion from value/name."""

        # Test enum members
        self._test_enum_members(AC.SwingMode)

        # Test fall back behavior to "OFF"
        enum = AC.SwingMode.get_from_name("NOT_A_SWING_MODE")
        self.assertEqual(enum, AC.SwingMode.OFF)
        self.assertIsInstance(enum, AC.SwingMode)

        # Test fall back behavior to "OFF"
        enum = AC.SwingMode.get_from_value(1234567)
        self.assertEqual(enum, AC.SwingMode.OFF)
        self.assertIsInstance(enum, AC.SwingMode)

    def test_swing_angle(self) -> None:
        """Test SwingAngle enum conversion from value/name."""

        # Test enum members
        self._test_enum_members(AC.SwingAngle)

        # Test fall back behavior to "OFF"
        enum = AC.SwingAngle.get_from_name("INVALID_NAME")
        self.assertEqual(enum, AC.SwingAngle.OFF)
        self.assertIsInstance(enum, AC.SwingAngle)

        # Test fall back behavior to "OFF"
        enum = AC.SwingAngle.get_from_value(1234567)
        self.assertEqual(enum, AC.SwingAngle.OFF)
        self.assertIsInstance(enum, AC.SwingAngle)

        # Test that converting from None works
        enum = AC.SwingAngle.get_from_value(None)
        self.assertEqual(enum, AC.SwingAngle.OFF)
        self.assertIsInstance(enum, AC.SwingAngle)

        enum = AC.SwingAngle.get_from_name(None)
        self.assertEqual(enum, AC.SwingAngle.OFF)
        self.assertIsInstance(enum, AC.SwingAngle)

        enum = AC.SwingAngle.get_from_name("")
        self.assertEqual(enum, AC.SwingAngle.OFF)
        self.assertIsInstance(enum, AC.SwingAngle)


class TestUpdateStateFromResponse(unittest.TestCase):
    """Test updating device state from responses."""

    def test_state_response(self) -> None:
        """Test parsing of StateResponses into device state."""

        # V3 state response
        TEST_RESPONSE = bytes.fromhex(
            "aa23ac00000000000303c00145660000003c0010045c6b20000000000000000000020d79")

        resp = Response.construct(TEST_RESPONSE)
        self.assertIsNotNone(resp)

        # Assert response is a state response
        self.assertEqual(type(resp), StateResponse)

        # Create a dummy device and process the response
        device = AC(0, 0, 0)
        device._update_state(resp)

        # Assert state is expected
        self.assertEqual(device.target_temperature, 21.0)
        self.assertEqual(device.indoor_temperature, 21.0)
        self.assertEqual(device.outdoor_temperature, 28.5)

        self.assertEqual(device.eco_mode, True)
        self.assertEqual(device.turbo_mode, False)
        self.assertEqual(device.freeze_protection_mode, False)
        self.assertEqual(device.sleep_mode, False)

        self.assertEqual(device.operational_mode, AC.OperationalMode.COOL)
        self.assertEqual(device.fan_speed, AC.FanSpeed.AUTO)
        self.assertEqual(device.swing_mode, AC.SwingMode.VERTICAL)
        self.assertEqual(device.turbo_mode, False)
        self.assertEqual(device.freeze_protection_mode, False)
        self.assertEqual(device.sleep_mode, False)

        self.assertEqual(device.operational_mode, AC.OperationalMode.COOL)
        self.assertEqual(device.fan_speed, AC.FanSpeed.AUTO)
        self.assertEqual(device.swing_mode, AC.SwingMode.VERTICAL)

    def test_properties_response(self) -> None:
        """Test parsing of PropertiesResponse into device state."""
        # https://github.com/mill1000/midea-ac-py/issues/60#issuecomment-1936976587
        TEST_RESPONSE = bytes.fromhex(
            "aa21ac00000000000303b10409000001000a00000100150000012b1e020000005fa3")

        resp = Response.construct(TEST_RESPONSE)
        self.assertIsNotNone(resp)

        # Assert response is a state response
        self.assertEqual(type(resp), PropertiesResponse)

        # Create a dummy device and process the response
        device = AC(0, 0, 0)
        device._update_state(resp)

        # Assert state is expected
        # TODO Test cases doesn't test values that differ from defaults
        self.assertEqual(device.horizontal_swing_angle, AC.SwingAngle.OFF)
        self.assertEqual(device.vertical_swing_angle, AC.SwingAngle.OFF)

    def test_properties_ack_response(self) -> None:
        """Test parsing of PropertiesResponse from SetProperties command into device state."""
        # https://github.com/mill1000/midea-msmart/issues/97#issuecomment-1949495900
        TEST_RESPONSE = bytes.fromhex(
            "aa18ac00000000000302b0020a0000013209001101000089a4")

        resp = Response.construct(TEST_RESPONSE)
        self.assertIsNotNone(resp)

        # Assert response is a state response
        self.assertEqual(type(resp), PropertiesResponse)

        # Create a dummy device and process the response
        device = AC(0, 0, 0)
        device._update_state(resp)

        # Assert state is expected
        self.assertEqual(device.horizontal_swing_angle, AC.SwingAngle.POS_3)
        self.assertEqual(device.vertical_swing_angle, AC.SwingAngle.OFF)


class TestSendCommand(unittest.IsolatedAsyncioTestCase):

    @patch("vogmidea.device.Device._send_command")
    async def test_response_ignore_bad_crc(self, mock_send_command) -> None:
        """Test that bad CRCs are ignored when in response to properties commands."""
        TEST_RESPONSE_BAD_CRC = bytes.fromhex(
            "aa14ac00000000000303b10109000001003c000042")
        TEST_RESPONSE_BAD_CHECKSUM = bytes.fromhex(
            "aa14ac00000000000303b10109000001003c0000FF")

        # Set return value of mocked method
        mock_send_command.return_value = [TEST_RESPONSE_BAD_CRC]

        # Create a dummy device
        device = AC(0, 0, 0)

        # Assert we start not ignoring CRCs
        self.assertEqual(device._disable_properties_crc_check, False)

        # Send a properties command
        command = GetPropertiesCommand([PropertyId.SWING_UD_ANGLE])
        responses = await device._send_command_get_responses(command)

        # Assert that responses are received
        self.assertTrue(responses)

        # Assert we start are now ignoring CRCs
        self.assertEqual(device._disable_properties_crc_check, True)

        # Check that we still check CRCs on non-properties commands
        with self.assertLogs("msmart") as log:
            command = GetStateCommand()
            responses = await device._send_command_get_responses(command)

            # Assert that no responses received
            self.assertFalse(responses)

        # Assert that an error was generated
        self.assertRegex(log.output[0], "^ERROR:.*Payload.*failed CRC")

        # Change mocked return to an invalid frame
        mock_send_command.return_value = [TEST_RESPONSE_BAD_CHECKSUM]

        # Assert that checksums are always checked regardless of command
        with self.assertLogs("msmart") as log:
            command = GetStateCommand()
            responses = await device._send_command_get_responses(command)

            # Assert that no responses received
            self.assertFalse(responses)

            # Send a properties command
            command = GetPropertiesCommand([PropertyId.SWING_UD_ANGLE])
            responses = await device._send_command_get_responses(command)

            # Assert that no responses received
            self.assertFalse(responses)

        # Assert that an error was generated
        self.assertRegex(log.output[0], "^ERROR:.*Frame.*failed checksum")
        self.assertRegex(log.output[1], "^ERROR:.*Frame.*failed checksum")


if __name__ == "__main__":
    unittest.main()

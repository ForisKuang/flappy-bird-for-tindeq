from typing import Dict
import struct
import uuid
import asyncio

import numpy as np

from bleak import BleakClient, BleakScanner


class ProgressorClient(object):
    cmds: dict[str, int] = {'TARE_SCALE': 100, 'START_WEIGHT_MEAS': 101, 'STOP_WEIGHT_MEAS': 102,
                            'START_PEAK_RFD_MEAS': 103, 'START_PEAK_RFD_MEAS_SERIES': 104, 'ADD_CALIB_POINT': 105,
                            'SAVE_CALIB': 106, 'GET_APP_VERSION': 107, 'GET_ERR_INFO': 108, 'CLR_ERR_INFO': 109,
                            'SLEEP': 110, 'GET_BATT_VLTG': 111}

    response_codes: dict[str, int] = {'RES_CMD_RESPONSE': 0, 'RES_WEIGHT_MEAS': 1, 'RES_RFD_PEAK': 2,
                                      'RES_RFD_PEAK_SERIES': 3,
                                      'RES_LOW_PWR_WARNING': 4}

    service_uuid = '7e4e1701-1ea6-40c9-9dcc-13d34ffead57'
    write_uuid = '7e4e1703-1ea6-40c9-9dcc-13d34ffead57'
    notify_uuid = '7e4e1702-1ea6-40c9-9dcc-13d34ffead57'

    def __init__(self, parent):
        """
        Uses Bluetooth 4 (LE) to communicate with Tindeq Progressor

        Send bytes to write UUID to control the device. Current weight or
        rate of force is reported on the notify UUID, so use callbacks to do
        something when you receive info on this UUID.

        Use as a context manager:

            >>> aysnc with ProgressorClient(parent) as tindeq:
            >>>     await tindeq.get_batt()

        Parameters
        ----------
        parent: object
            An owning class that implements callbacks specifying
            what to do when receiving weight notifications
        """
        self.parent = parent
        self.info_struct = struct.Struct("<bb")
        self.data_struct = struct.Struct("<fl")
        self._tare_value = 0.0

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *excinfo):
        await self.disconnect()

    def _notify_handler(self, sender: object, data: object) -> None:
        """
        Simply pass on payload to correct handler
        """
        data = bytes(data)
        kind, size = self.info_struct.unpack(data[:2])
        if kind == self.response_codes['RES_WEIGHT_MEAS']:
            # decode data
            for weight, useconds in self.data_struct.iter_unpack(data[2:]):
                now = useconds / 1.0e6
                self.parent.log_force_sample(now, weight - self._tare_value)
        elif kind == self.response_codes['RES_CMD_RESPONSE']:
            self._cmd_response(data)
        elif kind == self.response_codes['RES_LOW_PWR_WARNING']:
            print("low power warning")
        else:
            raise RuntimeError(f"unknown msg kind {kind}")

    def _cmd_response(self, value):
        if self.last_cmd == "get_app":
            print(f"FW version : {value[2:].decode('utf-8')}")
        elif self.last_cmd == "get_batt":
            (vdd,) = struct.unpack("<I", value[2:])
            print(f"Battery level = {vdd} [mV]")
        elif self.last_cmd == "get_err":
            try:
                print("Crashlog : {0}".format(value[2:].decode("utf-8")))
            except UnicodeDecodeError:
                pass
        self.last_cmd = None

    async def disconnect(self) -> None:
        await self._send_cmd("SLEEP")
        await self.client.disconnect()
        self.client = None

    async def connect(self) -> None:
        print("Searching for progressor...")
        scanner = BleakScanner()
        devices = await scanner.discover(timeout=20.0)
        TARGET_NAME = "Progressor"
        address = None
        for d in devices:
            if (
                    hasattr(d, 'name') and
                    (d.name is not None) and
                    (d.name[: len(TARGET_NAME)] == TARGET_NAME)):
                address = d.address
                print('Found "{0}" with address {1}'.format(d.name, d.address))
                break

        if address is None:
            raise RuntimeError("cannot find tindeq")

        self.client = BleakClient(address)
        await self.client.connect()
        success = self.client.is_connected
        if success:
            print('Connected to progressor with address {0}'.format(address))
            await self.client.start_notify(
                uuid.UUID(self.notify_uuid), self._notify_handler
            )
            print('Notified client')
        else:
            raise RuntimeError("could not connect to progressor")
        return success

    def _pack(self, cmd):
        return cmd.to_bytes(2, byteorder="little")

    async def _send_cmd(self, cmd_key):
        if not hasattr(self, "client") or self.client is None:
            return

        await self.client.write_gatt_char(
            uuid.UUID(self.write_uuid), self._pack(self.cmds[cmd_key])
        )

    async def get_batt(self):
        self.last_cmd = "get_batt"
        await self._send_cmd("GET_BATT_VLTG")

    async def get_fw_info(self):
        self.last_cmd = "get_app"
        await self._send_cmd("GET_APP_VERSION")

    async def get_err(self):
        self.last_cmd = "get_err"
        await self._send_cmd("GET_ERR_INFO")

    async def clear_err(self):
        self.last_cmd = None
        await self._send_cmd("CLR_ERR_INFO")

    async def start_logging_weight(self):
        self.last_cmd = None
        await self._send_cmd("START_WEIGHT_MEAS")

    async def stop_logging_weight(self):
        self.last_cmd = None
        await self._send_cmd("STOP_WEIGHT_MEAS")

    async def sleep(self):
        self.last_cmd = None
        await self._send_cmd("SLEEP")

    async def soft_tare(self):
        _saved_parent = self.parent
        self.parent = SampleAverage()
        await self.start_logging_weight()
        await asyncio.sleep(1)
        await self.stop_logging_weight()
        self._tare_value = self.parent.mean
        self.parent = _saved_parent


class SampleAverage:
    def __init__(self):
        self.weights = []

    def log_force_sample(self, time, weight):
        self.weights.append(weight)

    @property
    def mean(self):
        return np.mean(self.weights)


async def example():
    class Wrapper:
        def log_force_sample(self, time, weight):
            print(f"{time}: {weight}")

    wrap = Wrapper()
    async with ProgressorClient(wrap) as tindeq:
        await tindeq.get_batt()
        await asyncio.sleep(0.5)
        await tindeq.get_fw_info()
        await asyncio.sleep(0.5)
        await tindeq.get_err()
        await asyncio.sleep(0.5)
        await tindeq.clear_err()
        await asyncio.sleep(0.5)

        await tindeq.soft_tare()
        await asyncio.sleep(1)

        print('Logging Weight')
        await tindeq.start_logging_weight()

        # Normalize values from 0 to N via 0 to 1 taken from inputs
        # Sleep should last until condition is satisfied, flappy bird is dead
        await asyncio.sleep(10)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(example())

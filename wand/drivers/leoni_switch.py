""" Driver for Leoni eol/mol 1xn fibre switches 
Updated for UW's serial Leoni connection + channel count"""

import serial


class LeoniSwitch:
    def __init__(self, port='COM4', timeout = 1, simulation=False):
        """ timeout (in seconds) for not hanging on readline
         if there's no line to read."""

        self.simulation = simulation
        if simulation:
            self._num_channels = 7
            return

        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.port = port
        self.ser.open()

        self._num_channels = None
        self.get_num_channels()

    def get_num_channels(self):
        """ Returns the number of channels on the switch """
        if self.simulation:
            return self._num_channels

        if self._num_channels is None:
            self.ser.write("type?\r\n".encode())
            resp = self.ser.readline().strip().decode("utf-8")  # "eol 1xn"
            assert resp.startswith("eol 1x") or resp.startswith("mol 1x")
            self._num_channels = int(resp[6:])
        return self._num_channels

    def set_active_channel(self, channel):
        """ Sets the active channel.
        :param channel: int: the channel number to select, not zero-indexed
        """
        if channel < 1 or channel > self._num_channels:
            raise ValueError('Channel out of bounds')
        if not isinstance(channel, int):
            raise TypeError('Only integers are allowed')
        if self.simulation:
            return
        self.ser.write("ch{}\r\n".format(channel).encode())

    def get_active_channel(self):
        """ Returns the active channel number
        :return: the active channel, not zero-indexed
        """
        if self.simulation:
            return 1

        self.ser.write("ch?\r\n".encode())
        return int(self.ser.readline().strip())

    def get_firmware_rev(self):
        """ Returns a firmware revision string, such as 'v8.09' """
        if self.simulation:
            return "Leoni fibre switch simulator"

        self.ser.write("firmware?\r\n".encode())
        return self.ser.readline().strip().decode("utf-8")

    def ping(self):
        """ pings the object, not the serial connection"""
        if self.simulation:
            return True
        return bool(self.get_num_channels())

    def close(self):
        if self.simulation:
            return
        self.ser.close()

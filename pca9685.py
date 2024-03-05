import math
import time
import struct
from micropython import const


class PCA9685(object):
    MODE1 = const(0x00)
    MODE2 = const(0x01)
    SUBADR1 = const(0x02)
    SUBADR2 = const(0x03)
    SUBADR3 = const(0x04)
    PRESCALE = const(0xFE)
    LED0_ON_L = const(0x06)
    LED0_ON_H = const(0x07)
    LED0_OFF_L = const(0x08)
    LED0_OFF_H = const(0x09)
    ALL_LED_ON_L = const(0xFA)
    ALL_LED_ON_H = const(0xFB)
    ALL_LED_OFF_L = const(0xFC)
    ALL_LED_OFF_H = const(0xFD)

    def __init__(self, i2c, i2c_address=0x40) -> None:
        self._i2c_address = i2c_address
        self._i2c = i2c
        self._i2c.writeto_mem(self._i2c_address, PCA9685.MODE1, bytes([0x00]))
        self.frequency = 50
        for i in range(16):
            self.pwm(i, 0, 0)

    @property
    def frequency() -> None:
        return None

    @frequency.setter
    def frequency(self, frequency_hz) -> None:
        prescaler = 25000000.0  # 25MHz
        prescaler /= 4096.0  # 12-bit
        prescaler /= float(frequency_hz)
        prescaler -= 1.0
        prescaler = int(math.floor(prescaler + 0.5))

        old_mode = self._i2c.readfrom_mem(self._i2c_address, PCA9685.MODE1,
                                          1)[0]
        new_mode = (old_mode & 0x7F) | 0x10  # sleep
        self._i2c.writeto_mem(self._i2c_address, PCA9685.MODE1,
                              bytes([new_mode]))
        self._i2c.writeto_mem(self._i2c_address, PCA9685.PRESCALE,
                              bytes([prescaler]))
        self._i2c.writeto_mem(self._i2c_address, PCA9685.MODE1,
                              bytes([old_mode]))
        time.sleep(0.005)
        self._i2c.writeto_mem(self._i2c_address, PCA9685.MODE1,
                              bytes([old_mode | 0xA1]))

    def pwm(self, channel, on, off):
        if channel < 0 or channel > 15:
            raise ValueError(f"{channel} is out of range for channel (0-15)")

        if on < 0 or on > 4095:
            raise ValueError(f"{on} is out of range for on (0-4095)")

        if off < 0 or off > 4095:
            raise ValueError(f"{off} is out of range for off (0-4095)")

        self._i2c.writeto_mem(self._i2c_address,
                              (channel << 2) + PCA9685.LED0_ON_L,
                              struct.pack("<HH", on, off))

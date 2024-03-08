""" 
ina230.py

    Texas Instruments INA230 I2C Power Monitor device Lib

* Author: Caden Hillis
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import ROBits, RWBits

try:
    from typing import Union
    from busio import I2C
except ImportError:
    pass

# Device Register Map
_CFG_REG = const(0x0)
# _SHUNT_VOLTAGE_REG = const(0x1)
_BUS_VOLT_REG = const(0x2)
# _POWER_REG = const(0x3)
_CUR_REG = const(0x4)
_CAL_REG = const(0x5)
# _MASK_EN_REG = const(0x6)
# _ALERT_LIMIT_REG = const(0x7)
# _DIE_ID_REG = const(0xff)

# Device Default Register Values
_CFG_DEFAULT = const(0x4127)


class INA230:
    """
    class for controlling and reading INA230
        not all regs and functionality implemented
    """

    _cfg = RWBits(16, _CFG_REG, 0, register_width=2, lsb_first=False)
    _bus_volt = ROBits(15, _BUS_VOLT_REG, 0, register_width=2, lsb_first=False)
    _current = ROBits(16, _CUR_REG, 0, register_width=2, signed=True, lsb_first=False)
    _cal = RWBits(16, _CAL_REG, 0, register_width=2, signed=False, lsb_first=False)

    def __init__(
        self,
        i2c_bus: I2C,
        addr: int = 0x70,
        imax: Union[int, float] = 10,
        rshunt: Union[int, float] = 10,
    ):
        # imax is in amps
        # rshunt is in mR
        self.i2c_device = I2CDevice(i2c_bus, addr, probe=False)
        if not self._cfg == _CFG_DEFAULT:
            raise RuntimeError("[INA230.PY] INA230 not found")
        self._imax = imax
        self._rshunt = rshunt
        self._lsb = self._imax / 2**15
        self.calibrate()

    @property
    def bus_voltage(self) -> float:
        """bus voltage reading"""
        return self._bus_volt * 0.00125

    @property
    def current(self) -> float:
        """current reading"""
        cur = self._current
        if self.cal != 0:
            cur *= self._lsb
        return cur

    @property
    def cal(self) -> int:
        """device calibration value"""
        return self._cal

    def calibrate(self):
        """calibaration the device"""
        res = self._rshunt / 1000
        cal = 0.00512 / (self._lsb * res)
        cal = round(cal)
        if cal >= 2**16:
            cal = 0xFFFF
        self._cal = cal

import datetime
import random
from time import sleep

from VisualModbus.MbClient import MbClient
from VisualModbus.RegMap import RegMap
from RtdEmulRegs import RtdEmulRegs as Dut


# Open modbus client with given communication settings
mb = MbClient()
mb.open('ComSettings.json')

# Create device and load register maps
regs = RegMap(mb, 32)
regs.load("RtdEmul_Modbus.json")


def set_random_ntc(iterations=2, period=60, slew=10):
    """
    Verification case
    :param iterations: Number of On and Off Testing periods
    :param period: Time period between 2 measurements [s]
    :param slew: Temperature slew rate [K/s]
    :return: Number of errors
    """
    ret = 0

    # Set emulation mode to NTC
    regs.write_by_name(Dut.EMUL_MODE, 1)

    # Set slew rate
    regs.write_by_name(Dut.EMUL_SLEW_RATE, slew)

    # Read device serial number and firmware revision
    sn = regs.read_by_name(Dut.FACT_SERIAL_NUMBER)
    fw_ver = regs.read_by_name(Dut.FIRM_REVISION)

    print(f"=== NTC Emulator SN: {sn}, FW: {fw_ver}. Slew rate is set to {slew} K/s.")

    for itr in range(iterations):
        # Generate random parameters
        beta = random.randint(3000, 5500)
        stock = random.randint(1000, 10000)
        temp = random.uniform(-20, 250)

        # Write NTC parameters
        regs.write_by_name(Dut.EMUL_NTC_BETA, beta)
        regs.write_by_name(Dut.EMUL_NTC_STOCK_RES, stock)

        # Write requested temperature into all 4 channels
        regs.write_multi_name(Dut.EMUL_TEMPERATURE_1, [temp] * 4)

        print(f"=== Emulate NTC {stock} with beta {beta} at temperature {temp:.3f} C.")

        # Sleep for given time
        sleep(period)

    # Reset device to get into default state (not necessary)
    regs.write_by_name(Dut.SYS_COMMAND, 9901)

    return ret


if __name__ == "__main__":
    print(f"=== START === " + datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S ==="))
    err = 0

    err += set_random_ntc(iterations=2, period=30)

    print(f"=== END === " + datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S ==="))
    print('=== RESULT === {} === '.format('SUCCESS' if err == 0 else '{} ERRORS'.format(err)))

from time import sleep
from sys import stdout

# import own modules
from VisualModbus.AppLogging import *
from VisualModbus.RegMap import RegMap as rm
from VisualModbus.MbClient import MbClient
import VisualModbus.VmSettings as s

# Start logging into log file
log = AppLogging(logging.WARNING)
# Load settings from multiple JSONs
s.read_settings(['VisualSettings.json', 'UpgradeSettings.json', 'ComSettings.json'])
# Open modbus client connection
mb = MbClient()
mb.open('ComSettings.json')
# Create and load register map
regs = rm(mb, s.s['slave_address'])
regs.load(s.s['reg_map'])
# Define list of slave device addresses
units = [s.s['slave_address']]
errors = 0


def read_write_test(delay, iterations, slaves=None, verbosity=2):
    """
    Perform full test of modbus communication including exception
    :param delay: Delay between iterations in milliseconds
    :param iterations: Number of full test iterations
    :param slaves: Array of slave device addresses
    :param verbosity: Level of debug prints (0 - none, 1 - final report, 2 - each iteration)
    :return: Number of errors
    """
    global errors, units
    last_er = 0
    errors = 0
    if slaves is not None:
        units = slaves

    for itr in range(iterations):
        for unit in units:
            # Read all registers
            regs.read_in()
            regs.read_hold()

            # Try all unsupported function codes and exception codes
            rr = mb.client.read_coils(0, 10, unit=unit)
            assert_err(rr, "IllegalFunction")

            rr = mb.client.read_discrete_inputs(0, 10, unit=unit)
            assert_err(rr, "IllegalFunction")

            rr = mb.client.write_coil(1, True, unit=unit)
            assert_err(rr, "IllegalFunction")

            rr = mb.client.write_coils(0, [True] * 2, unit=unit)
            assert_err(rr, "IllegalFunction")

            rr = mb.client.write_register(1, 150, unit=unit)
            assert_err(rr, "IllegalFunction")

            rr = mb.client.read_input_registers(900, 10, unit=unit)
            assert_err(rr, "IllegalAddress")

            rr = mb.client.read_input_registers(0, 150, unit=unit)
            assert_err(rr, "IllegalValue")

            # Perform write and read back
            regs.write_by_name('SYS_TEST', itr)
            value = regs.read_by_name('SYS_TEST')
            if value != itr:
                errors += 1

            # Print status (must be stdout.write to make override possible)
            if verbosity >= 2:
                stdout.write("Test iteration number {0}, errors {1}, unit {2} \r".format(itr + 1, errors, unit))
                if errors != last_er:
                    stdout.write("\n")

            last_er = errors
            sleep(delay / 1000)
    if verbosity >= 2:
        stdout.write("\n")
    if verbosity >= 1:
        print('Read/Write @ {}, parity {}, {} stop bits. Result {}'.
              format(mb.s['baud_rate'], mb.s['parity'], mb.s['stop_bits'],
                     'OK' if errors == 0 else '{} ERRORS'.format(errors)))
    return errors


def read_write_reopen(baud_rate, parity, stop_bits):
    """
    Close and reopen communication port
    :param baud_rate: Baud rate to use
    :param parity: Parity ('N', 'E', or 'O')
    :param stop_bits: Number of stop bits
    :return: None
    """
    read_write_close()
    mb.s['baud_rate'] = baud_rate
    mb.s['parity'] = parity
    mb.s['stop_bits'] = stop_bits
    mb.open()


def read_write_close():
    """
    Close the communication port
    :return: None
    """
    mb.close()


def assert_ok(rr):
    """
    Assert that request response is not an error
    :param rr: Response
    :return: None (global errors incremented on error)
    """
    global errors
    if rr.isError():
        errors = errors + 1
        print(rr)


def assert_err(rr, exp):
    """
    Assert that request response contains given error message
    :param rr: Response
    :param exp: Expected error message part
    :return: None (global errors incremented on error)
    """
    global errors
    if not rr.isError():
        errors = errors + 1
    else:
        if exp not in str(rr):
            errors = errors + 1
            print(rr)


def assert_val(name, value, msg):
    """
    Assert that register given by name has expected value. If not, print the message
    :param name: Register name
    :param value: Expected value
    :param msg: Mismatch message
    :return: None (global errors incremented on error)
    """
    global errors
    val = regs.read_by_name(name)
    if val != value:
        print("ASSERT: " + msg + f": expected {value}, is: {val}")
        errors += 1


def get_errors():
    """
    Get number of errors
    :return: Number of errors
    """
    global errors
    return errors


if __name__ == "__main__":
    _delay = 1000
    _iterations = 2

    read_write_test(_delay, _iterations)
    read_write_close()

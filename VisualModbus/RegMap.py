import io
import json
import struct
from time import sleep


def _get_values_for_mb(reg):
    """
    Return modbus representation of register
    :param reg: Register
    :return: Array of 16-bit values for modbus
    """
    short_mask = ((1 << 16) - 1)
    if reg['Format'] == 'FLOAT':
        values = int(float(reg['Value']) * 10)
        values = values if values >= 0 else values + (1 << 16)
        values = [values]
    elif reg['Format'] == 'FLOAT32':
        number = struct.unpack('L', struct.pack('f', float(reg['Value'])))[0]
        values = [number & short_mask, number >> 16]
    elif reg['Format'] == 'STRING':
        number = bytearray(str(reg['Value']), encoding='utf-8')
        values = [0] * len(reg['Address'])
        for i in range(min(len(number), 2*len(reg['Address']))):
            values[i // 2] |= int(number[i]) << (8 * (i % 2))
    else:
        values = []
        for i in range(len(reg['Address'])):
            values.append((int(reg['Value']) >> (i * 16)) & short_mask)
    return values


def _set_value_from_mb(reg, values):
    """
    Set register value from modbus received values
    :param reg: Register
    :param values: Array of 16-bit numbers from modbus
    :return: None (value is updated within register)
    """
    if reg['Format'] == 'FLOAT':
        reg['Value'] = str(float(values[0] if values[0] < (1 << 15) else values[0] - (1 << 16)) / 10)
    elif reg['Format'] == 'FLOAT32':
        number = int(values[0]) + (int(values[1]) << 16)
        reg['Value'] = str(round(struct.unpack('f', struct.pack('L', number))[0], 4))
    elif reg['Format'] == 'STRING':
        buf = bytearray(len(values) * 2)
        for i in range(len(values)):
            buf[2*i + 0] = values[i] & 0xFF
            buf[2*i + 1] = values[i] >> 8
        reg['Value'] = buf.partition(b'\0')[0].decode('utf-8')
    else:
        temp_value = 0
        for i in range(len(values)):
            temp_value |= values[i] << (i * 16)
        reg['Value'] = str(temp_value)


def _get_value(reg):
    """
    Return value of register in proper format
    :param reg: Register
    :return: Float, integer or string value
    """
    if reg['Format'] == 'FLOAT' or reg['Format'] == 'FLOAT32':
        return float(reg['Value'])
    elif reg['Format'] == 'STRING':
        return reg['Value']
    else:
        return int(reg['Value'])


def _has_hex(reg):
    """
    Is register of integer type
    :param reg: Register
    :return: True for integers
    """
    if reg['Format'] in ('FLOAT', 'FLOAT32', 'STRING'):
        return False
    else:
        return True


class RegMap:
    """
    Modbus register map class
    """
    def __init__(self, mb, slave=1, attempts=2, delay=0.5):
        self.input = []
        self.hold = []
        self.wrReq = []
        self.rdReq = []
        self.max_len = 20
        self.hold_a = []
        self.input_a = []
        self.mb = mb
        self.slave = slave
        self.errors = 0
        self.bounds = 0
        self.last_write = None
        self.attempts = attempts
        self.delay = delay

    def load(self, filename):
        """
        Load register map from json file and sort them into input and holding groups
        :param filename: Json register map file
        :return: None
        """
        with io.open(filename, 'r', encoding='utf-8-sig') as f:
            regs = json.load(f)

        # Parse list of registers and count maximal address
        for reg in regs:
            self.max_len = max(self.max_len, len(reg['Name']) + 2)
            if 'Min' not in reg:
                reg['Min'] = 0
                reg['Max'] = 0
            if 'Label' not in reg:
                reg['Label'] = ""
            if 'Description' not in reg:
                reg['Description'] = ""
            if reg['Type'] == 'HOLD':
                self.hold.append(reg)
                if len(self.hold_a) != 0 and reg['Address'][0] == self.hold_a[-1][-1] + 1 and \
                        reg['Address'][-1] - self.hold_a[-1][0] < 123:
                    self.hold_a[-1][-1] = reg['Address'][-1]
                else:
                    self.hold_a.append([reg['Address'][0], reg['Address'][-1]])
            else:
                self.input.append(reg)
                if len(self.input_a) != 0 and reg['Address'][0] == self.input_a[-1][-1] + 1 and \
                        reg['Address'][-1] - self.input_a[-1][0] < 123:
                    self.input_a[-1][-1] = reg['Address'][-1]
                else:
                    self.input_a.append([reg['Address'][0], reg['Address'][-1]])

    def from_visual(self, values, suffix):
        """
        Create write request of values that changed its value in visual interface
        :param values: List of all values
        :param suffix: Suffix for HEX values
        :return: 0 on write success
        :return: None on write error
        """
        for reg in self.hold:
            write = 0
            new_val = values[reg['Name']]
            if reg['Value'] != new_val:
                write = 1
            elif _has_hex(reg):
                new_val = values[reg['Name'] + suffix]
                if new_val != self.val_to_hex(reg):
                    new_val = str(int(new_val.replace("0x", ""), 16))
                    write = 1
            if write != 0:
                reg['Value'] = new_val
                self._check_limits(reg)
                values_reg = _get_values_for_mb(reg)
                self.last_write = {'Address': reg['Address'][0], 'Count': len(values_reg), 'Values': values_reg,
                                   'Slave': self.slave}
                self.wrReq.append(self.last_write)

        if not self.wrReq and self.last_write is not None:
            self.wrReq.append(self.last_write)
        return self._send_write()

    def read_in(self):
        """
        Read all input registers and keep result in internal collection of registers
        :return: 0 on read success
        :return: None on read error
        """
        for rng in self.input_a:
            self.rdReq.append({'Address': rng[0], 'Count': rng[1] - rng[0] + 1, 'Type': 'Input', 'Slave': self.slave})
        return self._send_read()

    def read_hold(self):
        """
        Read all holding registers and keep result in internal collection of registers
        :return: 0 on read success
        :return: None on read error
        """
        for rng in self.hold_a:
            self.rdReq.append({'Address': rng[0], 'Count': rng[1] - rng[0] + 1, 'Type': 'Holding', 'Slave': self.slave})
        return self._send_read()

    def write_hold(self):
        """
        Write all holding registers one-by-one using their current values
        :return: 0 on write success
        :return: None on write error
        """
        for reg in self.hold:
            values_reg = _get_values_for_mb(reg)
            self.wrReq.append({'Address': reg['Address'][0], 'Count': len(values_reg), 'Values': values_reg,
                               'Slave': self.slave})
        return self._send_write()

    def from_modbus(self, request, values):
        """
        Store new values received from modbus in internal collection of registers
        :param request: Sent read request
        :param values: received list of values
        :return: None
        """
        address = request['Address']
        regs = self.input if request['Type'].lower() == 'Input'.lower() else self.hold
        for i in range(len(values)):
            reg = next(x for x in regs if (address + i) in x['Address'])
            pos = reg['Address'].index(address + i)
            regs_for_value = len(reg['Address'])
            if pos == 0:
                _set_value_from_mb(reg, values[i:i+regs_for_value])
                self._check_limits(reg)
                i += regs_for_value - 1

    def read_by_name(self, name):
        """
        Read register identified by name
        :param name: Register name
        :return: Register value on read success
        :return: None on read error
        """
        # Get register from list
        reg = self.get_by_name(name)
        ret = None
        attempt = 0
        # Read register with maximal number of attempts
        while ret is None and attempt < self.attempts:
            attempt += 1
            # Create read request and send it
            self.rdReq.append({'Address': reg['Address'][0], 'Count': len(reg['Address']), 'Type': reg['Type'],
                               'Slave': self.slave})
            ret = self._send_read()
            # Wait on error
            if ret is None:
                sleep(self.delay)
        if ret is None:
            return None
        else:
            self._check_limits(reg)
            return _get_value(reg)

    def write_by_name(self, name, value):
        """
        Write register identified by name
        :param name: Register name
        :param value: Register value
        :return: 0 on write success
        :return: None on write error
        """
        reg = self.get_by_name(name)
        # Set new value into register
        reg['Value'] = value
        self._check_limits(reg)
        values_reg = _get_values_for_mb(reg)
        ret = None
        attempt = 0
        # Write register with maximal number of attempts
        while ret is None and attempt < self.attempts:
            attempt += 1
            self.wrReq.append({'Address': reg['Address'][0], 'Count': len(values_reg), 'Values': values_reg,
                               'Slave': self.slave})
            ret = self._send_write()
            # Wait on error
            if ret is None:
                sleep(self.delay)
        return ret

    def write_multi_name(self, name, values):
        """
        Write multiple registers in a row if their names are indexed by number at the end
        :param name: Name of the first register (should end with _1)
        :param values: List of values to write to consecutive registers
        :return: None on fail
        """
        ret = 0
        for i in range(len(values)):
            if self.write_by_name(name[:-1] + str(i + 1), values[i]) is None:
                ret = None
        return ret

    def read_multi_name(self, name, count):
        """
        Read multiple registers in a row if their names are indexed by number at the end
        :param name: Name of the first register (should end with _1)
        :param count: Number of registers to read
        :return: List of read values
        """
        vals = []
        for i in range(count):
            vals.append(self.read_by_name(name[:-1] + str(i + 1)))
        return vals

    def get_by_name(self, name):
        """
        Get register by name
        :param name: Name of the register
        :return: Register
        """
        regs = self.input + self.hold
        return next(x for x in regs if x['Name'] == name)

    def val_to_hex(self, reg):
        """
        Get HEX string representation of register value
        :param reg: Register
        :return: HEX string
        """
        if reg['Format'] in ['FLOAT', 'FLOAT32', 'STRING']:
            return ""
        else:
            return hex(int(reg['Value']))

    def get_error_count(self, clear=1):
        """
        Return number of errors
        :param clear: Non-zero value clear the error count
        :return: number of errors
        """
        ret = self.errors
        if clear:
            self.errors = 0
        return ret

    def get_out_of_bound(self, clear=1):
        """
        Return number of out-of-bound errors
        :param clear: Non-zero value clear the out-of-band count
        :return: Number of out-of-band
        """
        ret = self.bounds
        if clear:
            self.bounds = 0
        return ret

    def reopen(self):
        """
        Reopen client port if closed
        :return: None
        """
        if not self.mb.client.is_socket_open():
            self.mb.open()

    def _check_limits(self, reg):
        """
        Check minimum and maximum limits of register
        :param reg: Register
        :return: None
        """
        if reg['Min'] != 0 and reg['Max'] != 0:
            if reg['Format'] == 'FLOAT' or reg['Format'] == 'FLOAT32':
                if float(reg['Value']) > reg['Max']:
                    self.bounds += 1
                    # reg['Value'] = str(reg['Max'])
                if float(reg['Value']) < reg['Min']:
                    self.bounds += 1
                    # reg['Value'] = str(reg['Min'])
            elif reg['Format'] == 'STRING':
                if len(reg['Value']) > reg['Max']:
                    self.bounds += 1
                if len(reg['Value']) < reg['Min']:
                    self.bounds += 1
            else:
                if int(reg['Value']) > reg['Max']:
                    self.bounds += 1
                    # reg['Value'] = str(reg['Max'])
                if int(reg['Value']) < reg['Min']:
                    self.bounds += 1
                    # reg['Value'] = str(reg['Min'])

    def _send_read(self):
        """
        Send read request to modbus slave and parse response
        :return: 0 on read success
        :return: None on read error
        """
        ret = 0
        for req in self.rdReq:
            registers = self.mb.read(req)
            if registers is not None:
                self.from_modbus(req, registers)
            else:
                ret = None
                self.errors += 1
                break
        self.rdReq.clear()
        return ret

    def _send_write(self):
        """
        Send write request to modbus slave and check response
        :return: 0 on write success
        :return: None on write error
        """
        ret = 0
        for req in self.wrReq:
            ret = self.mb.write_hold(req)
            if ret is None:
                self.errors += 1
                break
        self.wrReq.clear()
        return ret

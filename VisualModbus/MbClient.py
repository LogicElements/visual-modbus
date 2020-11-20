import io
import json
import logging

from pymodbus.client.sync import ModbusSerialClient as ModbusClient


class MbClient:
    """
    Class for communication with modbus client
    """

    def __init__(self):
        """
        Initialize all internal variables
        """
        self.errors = 0
        self.rr = None
        self.comport = None
        self.s = None
        self.client = ModbusClient()
        self.log = logging.getLogger()

    def open(self, settings=None):
        """
        Open com port with parameters given in JSON
        :param settings: Json settings file
        :return: True if connected, False on error
        """
        # Read settings JSON
        if settings is not None:
            with io.open(settings, 'r', encoding='utf-8-sig') as f:
                self.s = json.load(f)
        self.comport = self.s['comport']
        # Open port
        self.client = ModbusClient(method='rtu', port=self.s['comport'], timeout=self.s['timeout'],
                                   baudrate=self.s['baud_rate'], parity=self.s['parity'],
                                   stopbits=self.s['stop_bits'])
        # Set additional timeout parameters
        self.client.inter_char_timeout *= self.s['inter_char_timeout']  # default 0.000859375
        if 'minimal_inter_char_timeout' in self.s:
            min_inter = self.s['minimal_inter_char_timeout']
        else:
            min_inter = 0.05
        self.client.inter_char_timeout = max(self.client.inter_char_timeout, min_inter)
        self.client.silent_interval *= self.s['silent_interval']
        # Connect to port
        ret = self.client.connect()
        if ret is True:
            self.log.warning('Port {0} opened at baud rate {1}, parity {2}, stop bits {3}'.format(
                self.s['comport'], self.s['baud_rate'], self.s['parity'], self.s['stop_bits']))
        return ret

    def close(self):
        """
        Close communication port
        :return: None
        """
        self.log.warning('Port {} is closed now.'.format(self.comport))
        self.client.close()

    def read(self, request):
        """
        Send read request to slave device, parse response and return register values
        :param request: Request dictionary, such as {'Address': 50, 'Count': 5, 'Type': "INPUT", 'Slave': 1}
        :return: Array of read register values on success
        :return: None on read error
        """
        if not self.client.is_socket_open():
            self.log.warning('Port {} is not opened. Try to open the port first'.format(self.comport))
            if self.comport is None:
                return None
            if self.open() is False:
                return None
        if request['Type'].lower() == 'Input'.lower():
            return self.read_input(request)
        else:
            return self.read_hold(request)

    def read_input(self, request):
        """
        Send read Input register request to slave device, parse response and return register values
        :param request: Request dictionary, such as {'Address': 50, 'Count': 5, 'Type': "INPUT", 'Slave': 1}
        :return: Array of read register values on success
        :return: None on read error
        """
        self.rr = self.client.read_input_registers(request['Address'], request['Count'], unit=request['Slave'])
        if self.rr.isError():
            self.log.error(str(self.rr) + str(request))
            return None
        else:
            self.log.info('Read input registers from slave {} at address {}, count {}.'
                          .format(request['Slave'], request['Address'], request['Count']))
            return self.rr.registers

    def read_hold(self, request):
        """
        Send read Holding register request to slave device, parse response and return register values
        :param request: Request dictionary, such as {'Address': 50, 'Count': 5, 'Type': "INPUT", 'Slave': 1}
        :return: Array of read register values on success
        :return: None on read error
        """
        self.rr = self.client.read_holding_registers(request['Address'], request['Count'], unit=request['Slave'])
        if self.rr.isError():
            self.log.error(str(self.rr) + str(request))
            return None
        else:
            self.log.info('Read holding registers from slave {} at address {}, count {}.'
                          .format(request['Slave'], request['Address'], request['Count']))
            return self.rr.registers

    def write_hold(self, request):
        """
        Send write holding register request to slave device and verify response
        :param request: Request dictionary, such as 'Address': 50, 'Values': [10, 11, 12], 'Type': "HOLD", 'Slave': 1
        :return: 0 on success
        :return: None on fail
        """
        if not self.client.is_socket_open():
            self.log.warning('Port {} is not opened. Try to open the port first'.format(self.comport))
            if self.comport is None:
                return None
            if self.open() is False:
                return None
        self.rr = self.client.write_registers(request['Address'], request['Values'], unit=request['Slave'])
        if self.rr.isError():
            self.log.error(str(self.rr) + str(request))
            return None
        else:
            self.log.info('Write holding registers to slave {} at address {}, count {}.'
                          .format(request['Slave'], request['Address'], request['Count']))
            return 0

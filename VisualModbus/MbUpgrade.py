import json
import io
import logging
from time import sleep


class MbUpgrade:
    """
    Class for upgrading firmware through modbus RTU protocol
    """
    HEADER_LEN = 4
    OFFSET_LEN = 3
    FOOTER_LEN = 2
    log = logging.getLogger()
    progress = 0
    size = 1

    def __init__(self, settings, mb, slave=1):
        """
        Initialize upgrade module from given json
        :param settings: Json upgrade settings file
        :param mb: MbClient object
        :param slave: Slave address
        """
        with io.open(settings, 'r', encoding='utf-8-sig') as f:
            s = json.load(f)
        self.reqs = []
        self.align = s['align']
        self.LEN_UPG_PAGE = s['page_bytes']
        self.offset = s['address']
        self.type = s['type_binary']
        self.mode = s['mode_operation']
        self.init_delay = s['init_delay']
        if 'block_delay' not in s:
            s['block_delay'] = 0.0
        self.block_delay = s['block_delay']
        self.mb = mb
        self.errors = 0
        self.slave = slave

    def load_file(self, file_name):
        """
        Load firmware binary file and divide it into pages to send.
        Binary file is appended by 0 if its length does not match align parameter.
        :param file_name: Firmware filename
        :return: None
        """
        with io.open(file_name, 'rb') as f:
            content = f.read()
        if len(content) % self.align != 0:
            content += ((0).to_bytes(self.align - (len(content) % self.align), byteorder='little'))

        # Create and write header
        header = [self.type, self.mode, len(content) % (1 << 16), len(content) // (1 << 16)]
        self.reqs.append({'Address': self.offset, 'Count': len(header), 'Values': header, 'Slave': self.slave})

        self.size = int((len(content) + self.LEN_UPG_PAGE - 1)/self.LEN_UPG_PAGE)
        # iterate for each page
        for page in range(self.size):
            data_length = min(len(content) - page * self.LEN_UPG_PAGE, self.LEN_UPG_PAGE)
            page_data = [0] * (self.LEN_UPG_PAGE//2 + self.OFFSET_LEN + self.FOOTER_LEN)
            # swap data from bytes to 16-bit registers
            off = page * self.LEN_UPG_PAGE
            for i in range(data_length//2):
                page_data[i + self.OFFSET_LEN] = int.from_bytes(content[off + i * 2:off + i * 2 + 2], byteorder='little'
                                                                , signed=False)
            # Set offset and create request
            page_data[0] = self.LEN_UPG_PAGE
            page_data[1] = off & ((1 << 16)-1)
            page_data[2] = off >> 16
            page_data[-1] = 1
            self.reqs.append({'Address': self.offset + self.HEADER_LEN, 'Count': len(page_data),
                              'Values': page_data, 'Type': 'Holding', 'Slave': self.slave})

        self.log.info('Bin file {0} opened. Size {1} bytes, {2} pages'.format(file_name, len(content), self.size))

    def run_upgrade(self, progress_clb=None):
        """
        Run upgrade procedure.

        This function will iterate upgrade firmware handshake, until the whole file is flashed into device.
        Progress callback is called after every page.
        :param progress_clb: Progress callback
        :return: 0 on success
        :return: non-zero on error
        """
        self.errors = 0
        request = self.hand_shake(None, None)
        # For each packet in queue
        while request is not None:
            # Write packet into device with 2 tries
            response = None
            retries = 2
            while response is None and retries:
                response = self.mb.write_hold(request)
                retries -= 1
            # If this was start packet, wait some time
            if request['Address'] == self.offset and request['Count'] == 4 and response is not None:
                sleep(self.init_delay)
            #  Upgrade hand shake that returns next packet or terminates
            request = self.hand_shake(request, response)
            # Read the device status if its ready with 3 tries
            status_resp = None
            retries = 3
            if self.block_delay != 0:
                sleep(self.block_delay)
            while not self.check_status(status_resp) and retries:
                status_req = self.request_status()
                status_resp = self.mb.read(status_req)
                retries -= 1
            if not retries and not self.check_status(status_resp):
                self.terminate()
            if progress_clb is not None:
                progress_clb(self.progress, self.size)
        # Send apply request
        self.mb.write_hold(self.request_apply())
        return self.errors

    def hand_shake(self, request, response):
        """
        Upgrade firmware handshake procedure
        :param request: Previously sent write request dictionary
        :param response: Received response
        :return: Next request to send
        :return: None on error
        """
        # Obtained None as request means start
        if request is None:
            return self.reqs.pop(0)
        else:
            # Response None means writing error, terminate
            if response is None:
                self.terminate()
                return None
            else:
                # We have written data packet into device
                if request['Address'] == self.offset + self.HEADER_LEN:
                    self.progress += 1
                # Return next request if not the last
                if len(self.reqs) != 0:
                    return self.reqs.pop(0)
                else:
                    return None

    def request_status(self):
        """
        Create read status request
        :return: Read request to get status
        """
        status_address = self.offset + self.HEADER_LEN + self.OFFSET_LEN + self.LEN_UPG_PAGE//2
        return {'Address': status_address, 'Count': 1, 'Type': 'Holding', 'Slave': self.slave}

    def request_apply(self):
        """
        Create request to apply new firmware
        :return: Write request to apply
        """
        return {'Address': self.offset + 1, 'Count': 1, 'Values': [2], 'Slave': self.slave}

    def check_status(self, response):
        """
        Check the received status register
        :param response: Response of read status
        :return: True on success, False on fail
        """
        if response is not None:
            if response[0] in [1, 2]:
                return True
        return False

    def terminate(self):
        """
        Terminate upgrade procedure for some reason
        :return: None
        """
        self.log.info('Upgrade terminated. Remaining {0} pages'.format(len(self.reqs)))
        self.reqs.clear()
        self.progress = 0
        self.errors += 1



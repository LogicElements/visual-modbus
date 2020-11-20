# import build-in modules
import PySimpleGUI as SG
# import own modules
from VisualModbus.AppLogging import *
from VisualModbus.RegMap import RegMap
from VisualModbus.MbClient import MbClient
import VisualModbus.HelpAbout as Help
import VisualModbus.VmSettings as Setting
from VisualModbus.MbUpgrade import *


def _upgrade_callback(progress, size):
    """
    Upgrade firmware callback called after each page is acknowledged by device.
    :param progress: Number of bytes already written
    :param size: Complete size of firmware
    :return: None
    """
    SG.OneLineProgressMeter('Upgrade progress bar', progress, size, 'KEY_PROGRESS')


class VisualMbApp:
    """
    Class for visual modbus application based on simpleGui
    """
    # Literal constants
    HEX_SUFFIX = "_H"
    INF_SUFFIX = "_INFO_BTN"
    READ_SUFFIX = "_READ_BTN"
    UPG_FILE = '_UPG_FILE'

    def __init__(self, visual='VisualSettings.json', upgrade='UpgradeSettings.json', com='ComSettings.json'):
        """
        Initialize VisualModbus application.

        This function reads all necessary settings json files, initializes modbus register map and displays
        window layout.
        :param visual: Json containing visual settings
        :param upgrade: Json containing upgrade firmware settings
        :param com: Json containing communication settings
        """
        self.win_log = None
        self.win_info = None
        self.window = None
        self.upgrade = upgrade
        # Initialize internal modules
        self.mb = MbClient()
        self.log = AppLogging()
        # Read settings and load jsons
        Setting.read_settings([visual, upgrade, com])
        self.regs = RegMap(self.mb, Setting.s['slave_address'])
        self.regs.load(Setting.s['reg_map'])
        # Create and display window layout
        self._finalize()

    def handle(self):
        """
        Handle of GUI features.

        This function blocks until window is closed and handles all user logic of GUI.
        :return: None on exit
        """
        while True:
            to = max(min(Setting.s['readout_period'] * 1000, 1000), 1000)
            event, values = self.window.Read(timeout=to, timeout_key='_TIMEOUT_')
            if event in (None, 'Close'):
                self.mb.close()
                break
            if 'Write' in event:
                self._write_mb(values)
            if 'Write All' in event:
                self.regs.write_hold()
            if event in 'Read':
                self._read_mb()
            if event in 'About':
                Help.show_help()
            if event in 'B_COMPORT':
                if self.window['B_COMPORT'].GetText() == 'COM open':
                    if self.mb.open('ComSettings.json'):
                        self.window['B_COMPORT'].Update('COM close')
                else:
                    self.window['B_COMPORT'].Update('COM open')
                    self.mb.close()
            if event in 'Edit':
                Setting.edit(self.window.size)
                self.regs.slave = Setting.s['slave_address']
            if event in 'Upgrade' and values[self.UPG_FILE] is not '':
                self._upgrade(values[self.UPG_FILE])
            if event in 'Show Log':
                self.win_log = self._show_log()
            if self.INF_SUFFIX in event:
                if self.win_info is not None:
                    self.win_info.close()
                self.win_info = self._show_info(event.replace(self.INF_SUFFIX, ""))
            if self.READ_SUFFIX in event:
                self.regs.read_by_name(event.replace(self.READ_SUFFIX, ""))
                self._update_regs()
            if event not in (None, 'Close'):
                self.window['T_STATUS'].Update(self.log.lrl.get_one_liner())
                if self.win_log is not None:
                    event_log, values = self.win_log.Read(timeout=0)
                    if event_log in (None, 'Close'):
                        self.win_log = None
                    else:
                        self.win_log['T_LOG'].Update(self.log.lrl.get_record())

    def _read_mb(self):
        """
        Read all registers and update them in visual
        :return: None
        """
        self.regs.read_in()
        self.regs.read_hold()
        self._update_regs()

    def _write_mb(self, values):
        """
        Write all holding registers
        :param values: List of all values
        :return: None
        """
        self.regs.from_visual(values, self.HEX_SUFFIX)
        self._update_regs()

    def _update_regs(self):
        """
        Update values of registers in visual
        :return: None
        """
        for reg in self.regs.input + self.regs.hold:
            self.window[reg['Name']].Update(reg['Value'])
            self.window[reg['Name'] + self.HEX_SUFFIX].Update(self.regs.val_to_hex(reg))

    def _upgrade(self, file_name):
        """
        Initialize and run firmware upgrade procedure
        :param file_name: Binary file to upgrade
        :return: None
        """
        # initialize and get first packet obtaining info
        upg = MbUpgrade(self.upgrade, self.mb, slave=Setting.s['slave_address'])
        upg.load_file(file_name)
        upg.run_upgrade(_upgrade_callback)

    def _show_log(self):
        """
        Show window containing most recent log entries
        :return: Window object
        """
        lay = [[SG.Text(self.log.lrl.get_record(), key='T_LOG', size=(50, 35))]]
        return SG.Window('Status log', lay, resizable=True, auto_size_text=True, auto_size_buttons=True, finalize=True)

    def _show_info(self, name):
        """
        Show window containing information about given register
        :param name: Name of the register
        :return: Window object
        """
        text = json.dumps(self.regs.get_by_name(name), indent=4)
        text = text.replace("\\r\\n", "\n        ")
        lay = [[SG.Text(text)]]
        return SG.Window('Register information', lay, resizable=True, auto_size_text=True, finalize=True)

    def _finalize(self):
        """
        Create and display window layout
        :return: None
        """
        menu_def = [['&Settings', ['&Edit']], ['&Help', '&About'], ]
        layout = [[SG.Menu(menu_def)], ]
        col1 = []
        for reg in self.regs.input + self.regs.hold:
            line = [SG.Button("?", size=(2, 1), key=reg['Name'] + self.INF_SUFFIX, pad=(0, 0)),
                    SG.Button("R", size=(2, 1), key=reg['Name'] + self.READ_SUFFIX),
                    SG.Text(reg['Name'], size=(self.regs.max_len, 1), tooltip=reg['Label']),
                    SG.InputText('0', size=(20, 1), key=reg['Name']),
                    SG.InputText('0', size=(12, 1), key=reg['Name'] + self.HEX_SUFFIX)]
            if reg['Min'] != 0 and reg['Max'] != 0:
                line.append(SG.Text(f"({reg['Min']}, {reg['Max']})"))
            col1.append(line)

        layout.append([SG.Column(col1, key='C_REGS', scrollable=True, vertical_scroll_only=True,
                                 size=(Setting.s['width'] - 10, Setting.s['height']))])
        layout.append([SG.FileBrowse('Select file'), SG.Button('Upgrade'), SG.Input(key=self.UPG_FILE)])
        layout.append([SG.Submit('Write'),
                       SG.Button('Write All'),
                       SG.Button('Read'),
                       SG.Button('COM open', key='B_COMPORT'),
                       SG.Button('Show Log'), SG.Cancel('Close')])
        layout.append([SG.Text('Status', key='T_STATUS', size=(Setting.s['width'] // 8, None))])

        self.window = SG.Window('VisualModbus. Version: ' + Help.VERSION, layout, resizable=True, finalize=True)
        Setting.init_size(self.window.size)
        self._update_regs()


if __name__ == "__main__":
    vm = VisualMbApp()
    vm.handle()


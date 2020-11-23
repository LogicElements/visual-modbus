from dirsync import sync

action = 'sync'     # sync, diff, or update
# action = 'diff'
common_ignore = ["log", "__pycache__"]
common_dev = ["Visual\\S+.py", "\\S+Settings.json", "SimpleVerif\\S+.py"]


visual_source = '../../le-py-core/le-core/VisualModbus/'
visual_target = '../VisualModbus/'

emul_source = '../../le-fw-rtd-emulator/Tests/RtdEmul/'
emul_target = '../RtdEmulator/'
emul_dev = ["RtdEmul_Modbus.json", "RtdEmulRegs.py"] + common_dev

phase_source = '../../le-fw-phase-det/Tests/PhaseDet/'
phase_target = '../PhaseDetector/'
phase_dev = ["PhaseDet_Modbus", "PhaseDetRegs"] + common_dev

rtd_source = '../../le-fw-vms-rtd/Tests/Vms_rtd/'
rtd_target = '../RtdMeter/'
rtd_dev = ["VMS_RTD_Modbus", "VMS_RTDRegs"] + common_dev

sync(visual_source, visual_target, action, ignore=common_ignore)

sync(emul_source, emul_target, action, ignore=common_ignore, only=emul_dev)

sync(phase_source, phase_target, action, ignore=common_ignore, only=phase_dev)

sync(rtd_source, rtd_target, action, ignore=common_ignore, only=rtd_dev)


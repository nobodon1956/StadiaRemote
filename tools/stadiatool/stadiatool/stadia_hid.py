"""
stadia_hid.py - Windows HID backend for stadiatool using hidapi (hid.dll).

The original hid.py (now hid_pyusb.py) uses PyUSB interrupt transfers, which do
not work on Windows because the OS HID driver claims the device and libusb
cannot do interrupt I/O on it. This module provides the same public interface
(HID class with write_report / read_report) on top of the native Windows HID
stack via the `hidapi` pip package - the same path Chrome's WebHID uses.
"""

import hid as _hidapi
import ctypes
from ctypes import wintypes

class HIDError(Exception):
    """HID error"""

class HIDTimeoutError(HIDError):
    """Error if a timeout occurs"""

# ---------------------------------------------------------------------------
# Windows HID caps via hid.dll (to learn the exact output report length)
# ---------------------------------------------------------------------------

_hid_dll = None
def _load_hid_dll():
    global _hid_dll
    if _hid_dll is None:
        _hid_dll = ctypes.WinDLL('hid.dll')
        _hid_dll.HidD_GetPreparsedData.restype = wintypes.BOOL
        _hid_dll.HidD_GetPreparsedData.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE)]
        _hid_dll.HidD_FreePreparsedData.restype = wintypes.BOOL
        _hid_dll.HidD_FreePreparsedData.argtypes = [wintypes.HANDLE]
        _hid_dll.HidP_GetCaps.restype = ctypes.c_long  # HIDP_STATUS
        _hid_dll.HidP_GetCaps.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    return _hid_dll

class _HIDP_CAPS(ctypes.Structure):
    _fields_ = [
        ('Usage', wintypes.USHORT),
        ('UsagePage', wintypes.USHORT),
        ('InputReportByteLength', wintypes.USHORT),
        ('OutputReportByteLength', wintypes.USHORT),
        ('FeatureReportByteLength', wintypes.USHORT),
        ('Reserved', wintypes.USHORT * 17),
        ('NumberLinkCollectionNodes', wintypes.USHORT),
        ('NumberInputButtonCaps', wintypes.USHORT),
        ('NumberInputValueCaps', wintypes.USHORT),
        ('NumberInputDataIndices', wintypes.USHORT),
        ('NumberOutputButtonCaps', wintypes.USHORT),
        ('NumberOutputValueCaps', wintypes.USHORT),
        ('NumberOutputDataIndices', wintypes.USHORT),
        ('NumberFeatureButtonCaps', wintypes.USHORT),
        ('NumberFeatureValueCaps', wintypes.USHORT),
        ('NumberFeatureDataIndices', wintypes.USHORT),
    ]

def _win_output_report_length(device_path):
    """Query OutputReportByteLength for a HID device path using hid.dll."""
    try:
        dll = _load_hid_dll()
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        GENERIC_READ = 0x80000000
        GENERIC_WRITE = 0x40000000
        FILE_SHARE_READ = 0x1
        FILE_SHARE_WRITE = 0x2
        OPEN_EXISTING = 3
        handle = kernel32.CreateFileW(
            device_path, GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE, None,
            OPEN_EXISTING, 0, None)
        if handle == -1 or handle == 0xFFFFFFFFFFFFFFFF:
            return None
        try:
            preparsed = wintypes.HANDLE()
            if not dll.HidD_GetPreparsedData(handle, ctypes.byref(preparsed)) or not preparsed:
                return None
            try:
                caps = _HIDP_CAPS()
                if dll.HidP_GetCaps(preparsed, ctypes.byref(caps)) == 1:  # HIDP_STATUS_SUCCESS
                    return caps.OutputReportByteLength
                return None
            finally:
                dll.HidD_FreePreparsedData(preparsed)
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return None

# ---------------------------------------------------------------------------
# HID interface compatible with the original hid.py
# ---------------------------------------------------------------------------

class HID:
    MAX_REPORT_SIZE = 4096

    dev = None
    out_len = None

    def __init__(self, device):
        """device: usb.core.Device (only idVendor/idProduct are used)."""
        vid = device.idVendor
        pid = device.idProduct

        infos = _hidapi.enumerate(vid, pid)
        if not infos:
            raise HIDError(f'No HID device found for {vid:04x}:{pid:04x}')

        # prefer vendor-defined usage (0xFF00) - NXP SDP/Flashloader interface
        info = infos[0]
        for i in infos:
            if (i.get('usage_page') or 0) == 0xFF00:
                info = i
                break

        path = info['path']
        if isinstance(path, str):
            path = path.encode('utf-8') + b'\0'

        self.dev = _hidapi.device()
        try:
            self.dev.open_path(path)
        except Exception as e:
            raise HIDError(f'Failed to open HID device {vid:04x}:{pid:04x}: {e}')

        # exact output report length required by WriteFile on Windows
        out_len = _win_output_report_length(path)
        if not out_len or out_len < 1:
            # NXP SDP data report is 1 + 1024 bytes
            out_len = 1025
        self.out_len = out_len

    def write_report(self, report):
        data = bytes(report)
        if len(data) < self.out_len:
            data = data + b'\x00' * (self.out_len - len(data))
        n = self.dev.write(data)
        if n < 0:
            raise HIDError('hid_write failed')
        return n

    def read_report(self, wait=None):
        # non-blocking read when no wait time given
        if not wait:
            data = self.dev.read(HID.MAX_REPORT_SIZE, 0)
            return bytes(data) if data else None

        timeout_ms = max(1, int(wait * 1000))
        data = self.dev.read(HID.MAX_REPORT_SIZE, timeout_ms)
        if not data:
            raise HIDTimeoutError('read_report timed out, try replugging the device')
        return bytes(data)

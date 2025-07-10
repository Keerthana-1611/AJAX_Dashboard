import wmi
import serial.tools.list_ports
import pythoncom


def is_pendrive_connected(serial_number):
    pythoncom.CoInitialize()
    c = wmi.WMI()
    for usb in c.Win32_DiskDrive(InterfaceType="USB"):
        if serial_number.lower() in usb.PNPDeviceID.lower():
            return True
    return False


def find_com_port_by_name(search_term):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if search_term.lower() in port.description.lower() or search_term.lower() in port.manufacturer.lower():
            return port.device  # e.g., 'COM3'
    return None

def list_usb_serials():
    c = wmi.WMI()
    for usb in c.Win32_DiskDrive(InterfaceType="USB"):
        print("Device:", usb.Caption)
        print("PNP ID:", usb.PNPDeviceID)
        print("-" * 40)

# # list_usb_serials()
# print("Pendrive is present: ",is_pendrive_connected('ABC00253'))
# print("Converter presenr ? > ",find_com_port_by_name("FTDI"))



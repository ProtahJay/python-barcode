import socket
import time
import os
import atexit
import glob
import json
import xml.etree.ElementTree as ET
from datetime import datetime

BUFFER_SIZE = 4096  # Adjust the size if needed
SAVE_PATH = r"C:\Users\ctisjw1\Desktop\scan_databases"

def get_data_from_xml(file_path):
    if not os.path.exists(file_path):
        return []

    tree = ET.parse(file_path)
    root = tree.getroot()
    data_list = []

    for scan in root.findall('Scan'):
        timestamp = scan.find('Timestamp').text
        data = scan.find('Data').text
        data_list.append({"Timestamp": timestamp, "Data": data})
    
    return data_list

def save_daily_data_to_xml(data, scanner_name):
    scanner_save_path = os.path.join(SAVE_PATH, scanner_name)
    os.makedirs(scanner_save_path, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"barcode_data_{date_str}.xml"
    file_path = os.path.join(scanner_save_path, filename)

    if not os.path.exists(file_path):
        root = ET.Element("BarcodeData")
        tree = ET.ElementTree(element=root)
        tree.write(file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scan_element = ET.SubElement(root, "Scan")
    timestamp_element = ET.SubElement(scan_element, "Timestamp")
    timestamp_element.text = timestamp_str
    data_element = ET.SubElement(scan_element, "Data")
    data_element.text = data

    tree.write(file_path)

    print(f"[+] Data saved to: {file_path}")

def read_scanner_data(scanner_socket, scanner_name):
    data_buffer = ""
    scanner_socket.settimeout(0.1)

    while True:
        try:
            data = scanner_socket.recv(BUFFER_SIZE)
            if data:
                data_buffer += data.decode("utf-8")

        except socket.timeout:
            if data_buffer:
                decoded_data = data_buffer.strip()
                print(f"[+] Received: {decoded_data}")
                save_daily_data_to_xml(decoded_data, scanner_name)
                data_buffer = ""

        except KeyboardInterrupt:
            print("\n[!] Keyboard interrupt. Stopping the scanner reading.")
            break

def start_scanner(ip, port, scanner_name):
    scanner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scanner_socket.connect((ip, port))
    print(f"[+] Connected to the barcode scanner at {ip}:{port}")

    try:
        read_scanner_data(scanner_socket, scanner_name)
    finally:
        scanner_socket.close()

from flask import Flask, render_template, request, redirect, url_for
import threading
import socket
import os
import input
from input import start_scanner, get_data_from_xml  # Import get_data_from_xml
import xml.etree.ElementTree as ET
from datetime import datetime  # Add this line

# Function to read data from the XML file
def read_data_from_xml(save_path, scanner_id):
    xml_file = os.path.join(save_path, f"scanner_data-{scanner_id}.xml")

    if not os.path.exists(xml_file):
        return []

    tree = ET.parse(xml_file)
    root = tree.getroot()

    scanner_data = []

    for data_element in root.findall("Data"):
        scanner_data.append(data_element.text)

    return scanner_data

app = Flask(__name__)

@app.route("/")
def index():
    # I added the "id" key to the available_scanners dictionary
    available_scanners = {
        1: {"id": 1, "name": "OCC-4A", "ip": "172.16.99.30", "port": 9898},
        2: {"id": 2, "name": "OCC-4B", "ip": "172.16.99.31", "port": 9898},
        3: {"id": 3, "name": "OCC-4C", "ip": "172.16.99.32", "port": 9898},
        4: {"id": 4, "name": "OCC-4D", "ip": "172.16.99.33", "port": 9898},
    }
    
    return render_template("index.html", barcode_scanners=available_scanners.values())

@app.route('/selected_scanners', methods=['POST'])
def selected_scanners():
    scanner_ids = [int(scanner_id) for scanner_id in request.form.getlist('scanners')]

    available_scanners = {
        1: {"id": 1, "name": "OCC-4A", "ip": "172.16.99.30", "port": 9898},
        2: {"id": 2, "name": "OCC-4B", "ip": "172.16.99.31", "port": 9898},
        3: {"id": 3, "name": "OCC-4C", "ip": "172.16.99.32", "port": 9898},
        4: {"id": 4, "name": "OCC-4D", "ip": "172.16.99.33", "port": 9898},
    }

    selected_scanners = []

    for scanner_id in scanner_ids:
        if scanner_id in available_scanners:
            selected_scanners.append(available_scanners[scanner_id])

    return render_template("selected_scanners.html", scanners=selected_scanners)

@app.route("/display_scanner_data/", defaults={"scanner_id": None})
@app.route("/display_scanner_data/<scanner_id>/")
def display_scanner_data(scanner_id):
    if scanner_id is None:
        return redirect(url_for("index"))

    scanner_id = int(scanner_id)

    available_scanners = {
        1: {"id": 1, "name": "OCC-4A", "ip": "172.16.99.30", "port": 9898},
        2: {"id": 2, "name": "OCC-4B", "ip": "172.16.99.31", "port": 9898},
        3: {"id": 3, "name": "OCC-4C", "ip": "172.16.99.32", "port": 9898},
        4: {"id": 4, "name": "OCC-4D", "ip": "172.16.99.33", "port": 9898},
    }

    scanner_data = []

    if scanner_id in available_scanners:
        scanner = available_scanners[scanner_id]
        
        # Pass the scanner_id when calling start_scanner
        scanner_thread = threading.Thread(target=start_scanner, args=(scanner["ip"], scanner["port"], scanner["name"]), daemon=True)
        scanner_thread.start()

        # Get scanner_data from the XML
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"barcode_data_{date_str}.xml"
        file_path = os.path.join(input.SAVE_PATH, scanner["name"], filename)
        scanner_data = get_data_from_xml(file_path)

    return render_template("display_scanner_data.html", scanner_data=scanner_data)

if __name__ == "__main__":
    app.run(debug=True)

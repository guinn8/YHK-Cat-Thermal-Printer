import socket
from time import sleep
from img_processing import *
import json
import socket

def initialize_printer(sock):
    """Initialize the printer to its default state."""
    sock.send(b"\x1b\x40")

def get_printer_status(sock):
    """Get the printer status."""
    sock.send(b"\x1e\x47\x03")
    return sock.recv(38)

def get_printer_serial_number(sock):
    """Get the printer's serial number."""
    sock.send(b"\x1D\x67\x39")
    return sock.recv(21)

def get_printer_product_info(sock):
    """Get the printer's product information."""
    sock.send(b"\x1d\x67\x69")
    return sock.recv(16)

def send_start_print_sequence(sock):
    """Start a print sequence."""
    sock.send(b"\x1d\x49\xf0\x19")

def send_end_print_sequence(sock):
    """End a print sequence."""
    sock.send(b"\x0a\x0a\x0a\x0a")

def print_image(sock, img):
    buf = format_image(img)
    initialize_printer(sock)  
    sleep(0.5)    
    send_start_print_sequence(sock)
    sleep(0.5)
    sock.send(buf)
    sleep(0.5)
    send_end_print_sequence(sock)
    sleep(0.5)

def get_printer_data(sock):
    """
    Collect static data from the printer and return it as a JSON object.

    Parameters:
    sock (socket.socket): The socket connected to the printer.

    Returns:
    dict: JSON-compatible dictionary containing the printer's data.
    """
    data = {}
    
    try:
        # Collect printer status
        print("Retrieving printer status...")
        status = get_printer_status(sock)
        if status:
            status_str = status.decode('ascii', errors='ignore')
            print(status_str)

            # Extract hardware and software versions based on known keywords
            hardware_version = status_str.split("HV=")[1].split(",")[0].strip()
            software_version = status_str.split("SV=")[1].split(",")[0].strip()

            # Find and parse voltage
            voltage_match = status_str.split("VOLT=")
            if len(voltage_match) > 1:
                voltage_str = voltage_match[1].split("mv")[0].strip()
                if voltage_str.isdigit():
                    voltage = f"{int(voltage_str) / 1000}V"
                else:
                    voltage = "Unknown"
            else:
                voltage = "Unknown"

            # Extract DPI
            dpi = status_str.split("DPI=")[1].split(",")[0].strip()
            
            data['printer_status'] = {
                "hardware_version": hardware_version,
                "software_version": software_version,
                "voltage": voltage,
                "dpi": dpi
            }
        else:
            data['printer_status'] = None

        # Collect printer serial number
        print("Retrieving serial number...")
        serial_number = get_printer_serial_number(sock)
        if serial_number and len(serial_number) == 21:
            data['serial_number'] = serial_number.decode('ascii').replace('\x00', '').strip()
        else:
            data['serial_number'] = None

        # Collect printer product information
        print("Retrieving product info...")
        product_info = get_printer_product_info(sock)
        if product_info and len(product_info) == 16:
            data['product_info'] = product_info.decode('ascii').replace('\x00', '').strip()
        else:
            data['product_info'] = None

    except Exception as e:
        print(f"Error retrieving data: {e}")
        data['error'] = str(e)

    # Return formatted JSON
    return json.dumps(data, indent=4)

def run_functional_tests(sock):
    """
    Run a suite of functional tests on defined printer commands.

    Parameters:
    sock (socket.socket): The socket connected to the printer.
    """
    # Test Cases
    tests = [
        {
            'name': 'Initialize Printer',
            'function': initialize_printer,
            'description': 'Initialize the printer to its default state.'
        },
        {
            'name': 'Get Printer Status',
            'function': get_printer_status,
            'description': 'Retrieve the current status of the printer.',
            'response_length': 38
        },
        {
            'name': 'Get Serial Number',
            'function': get_printer_serial_number,
            'description': 'Retrieve the printer\'s serial number.',
            'response_length': 21
        },
        {
            'name': 'Get Product Info',
            'function': get_printer_product_info,
            'description': 'Retrieve the printer\'s product information.',
            'response_length': 16
        },
        {
            'name': 'Start Print Sequence',
            'function': send_start_print_sequence,
            'description': 'Start the printing sequence.'
        },
        {
            'name': 'End Print Sequence',
            'function': send_end_print_sequence,
            'description': 'End the printing sequence.'
        }
    ]

    test_results = []

    for test in tests:
        print(f"Running Test: {test['name']}")
        print(test['description'])
        
        try:
            # Execute the function and optionally check the response
            result = test['function'](sock)
            if 'response_length' in test:
                # Display the response if length matches expected response length
                if len(result) == test['response_length']:
                    print(f"Response: {result}")
                    test_results.append({'Test': test['name'], 'Result': 'Passed', 'Data': result})
                else:
                    print(f"Unexpected Response Length: Expected {test['response_length']}, Got {len(result)}")
                    test_results.append({'Test': test['name'], 'Result': 'Failed (Response length mismatch)', 'Data': result})
            else:
                test_results.append({'Test': test['name'], 'Result': 'Passed'})
                
        except Exception as e:
            print(f"Error during {test['name']}: {e}")
            test_results.append({'Test': test['name'], 'Result': 'Failed (Exception)', 'Data': None})
        
        sleep(0.5)  # Small delay before next test

    # Print summary of test results
    print("Test Summary:")
    for result in test_results:
        print(f"{result['Test']}: {result['Result']}")
        if 'Data' in result and result['Data'] is not None:
            print(f"Data: {result['Data']}")

    # Optionally, log the results to a file
    with open('test_results.txt', 'w') as f:
        f.write("Printer Functional Test Results:\n")
        for result in test_results:
            f.write(f"{result['Test']}: {result['Result']}\n")
            if 'Data' in result and result['Data'] is not None:
                f.write(f"Data: {result['Data']}\n")

    print("Testing completed. Results have been saved to 'test_results.txt'.")
# FILENAME: main.py DO NOT REMOVE COMMENT

import bluetooth
import sys
from time import sleep
from printer import initialize_printer, get_printer_status, get_printer_serial_number, get_printer_product_info, send_start_print_sequence, send_end_print_sequence
from img_processing import create_text, print_image
import PIL.Image

printerMACAddress = '24:00:11:00:00:D3'
port = 2  # Ensure this is the correct RFCOMM port for your printer

def main():
    print("Connecting to printer...")
    
    # Establish Bluetooth connection
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((printerMACAddress, port))
        print("Connected to printer.")
        
        # Initialize printer and fetch info
        status = get_printer_status(sock)
        print("Printer Status:", status)
        sleep(0.5)
        
        serial_number = get_printer_serial_number(sock)
        print("Serial Number:", serial_number)
        sleep(0.5)
        
        product_info = get_printer_product_info(sock)
        print("Product Info:", product_info)
        sleep(0.5)
        
        # Determine if data is being piped in
        if not sys.stdin.isatty():
            print("Reading input from stdin...")
            input_text = sys.stdin.read()
            if input_text.strip():
                img = create_text(input_text, font_size=40)
            else:
                print("No input received from stdin.")
                sock.close()
                return
        else:
            # Read Image File
            try:
                img = PIL.Image.open("Turtle.jpg")
            except IOError:
                print("Failed to open 'Turtle.jpg'. Please provide input via stdin or ensure the image file exists.")
                sock.close()
                return
        
        print_image(sock, img)
        print("Image sent to printer.")
        
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Bluetooth connection failed: {err}")
    finally:
        sock.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()

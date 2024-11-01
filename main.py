# FILENAME: cli_printer.py DO NOT REMOVE COMMENT

import bluetooth
import sys
import argparse
from time import sleep
from printer import *
from img_processing import create_text
import PIL.Image

def connect_printer(mac_address, port):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mac_address, port))
    return sock

def close_printer(sock):
    sock.close()

def handle_status(sock):
    status = get_printer_status(sock)
    print("Printer Status:", status)

def handle_info(sock):
    serial_number = get_printer_serial_number(sock)
    print("Serial Number:", serial_number)
    product_info = get_printer_product_info(sock)
    print("Product Info:", product_info)

def handle_print_text(sock, text):
    img = create_text(text, font_size=40)
    print_image(sock, img)
    print("Text sent to printer.")

def handle_print_image(sock, image_path):
    try:
        img = PIL.Image.open(image_path)
        print_image(sock, img)
        print("Image sent to printer.")
    except IOError:
        print(f"Failed to open '{image_path}'. Please ensure the image file exists.")

def main():
    parser = argparse.ArgumentParser(description="CLI for Bluetooth Printer")
    parser.add_argument('--mac_address', required=True, help="MAC address of the printer")
    parser.add_argument('--port', type=int, required=True, help="RFCOMM port number for the printer")
    parser.add_argument('--status', action='store_true', help="Get printer status")
    parser.add_argument('--info', action='store_true', help="Get printer information")
    parser.add_argument('--text', help="Text to print")
    parser.add_argument('--image', help="Path to image file to print")
    args = parser.parse_args()

    try:
        print("Connecting to printer...")
        sock = connect_printer(args.mac_address, args.port)
        print("Connected to printer.")

        if args.status:
            print(get_printer_data(sock))
        elif args.info:
            handle_info(sock)
        elif not sys.stdin.isatty():
            input_text = sys.stdin.read()
            if input_text.strip():
                handle_print_text(sock, input_text)
            else:
                print("No input received from stdin.")
        elif args.text:
            handle_print_text(sock, args.text)
        elif args.image:
            handle_print_image(sock, args.image)
        else:
            print("No valid command provided. Use --status, --info, --text, or --image.")
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Bluetooth connection failed: {err}")
    finally:
        close_printer(sock)
        print("Connection closed.")

if __name__ == "__main__":
    main()
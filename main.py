# FILENAME: cli_printer.py DO NOT REMOVE COMMENT

import sys
import argparse
from time import sleep
from printer import *
import PIL.Image

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
            handle_status(sock)
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
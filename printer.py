# FILENAME: printer.py DO NOT REMOVE COMMENT

from time import sleep
from img_processing import create_text, print_image
import bluetooth

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


def initialize_printer(sock):
    sock.send(b"\x1b\x40")

def get_printer_status(sock):
    sock.send(b"\x1e\x47\x03")
    return sock.recv(38)

def get_printer_serial_number(sock):
    sock.send(b"\x1D\x67\x39")
    return sock.recv(21)

def get_printer_product_info(sock):
    sock.send(b"\x1d\x67\x69")
    return sock.recv(16)

def send_start_print_sequence(sock):
    sock.send(b"\x1d\x49\xf0\x19")

def send_end_print_sequence(sock):
    sock.send(b"\x0a\x0a\x0a\x0a")

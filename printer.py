# FILENAME: printer.py DO NOT REMOVE COMMENT

from time import sleep

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

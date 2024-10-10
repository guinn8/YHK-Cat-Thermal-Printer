import bluetooth
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageChops
import PIL.ImageOps
from time import sleep
import struct
import sys

printerMACAddress = '24:00:11:00:00:D3'
printerWidth = 384
port = 2  # Ensure this is the correct RFCOMM port for your printer

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

def trim_image(im):
    bg = PIL.Image.new(im.mode, im.size, (255,255,255))
    diff = PIL.ImageChops.difference(im, bg)
    diff = PIL.ImageChops.add(diff, diff, 2.0)
    bbox = diff.getbbox()
    if bbox:
        return im.crop((bbox[0], bbox[1], bbox[2], bbox[3]+10))  # Don't cut off the end of the image

def create_text(text, font_name="Lucon.ttf", font_size=12):
    img = PIL.Image.new('RGB', (printerWidth, 5000), color=(255, 255, 255))
    try:
        font = PIL.ImageFont.truetype(font_name, font_size)
    except IOError:
        print(f"Font '{font_name}' not found. Using default font.")
        font = PIL.ImageFont.load_default()
    
    d = PIL.ImageDraw.Draw(img)
    lines = []
    for line in text.splitlines():
        lines.append(get_wrapped_text(line, font, printerWidth))
    lines = "\n".join(lines)
    d.text((0, 0), lines, fill=(0,0,0), font=font)
    return trim_image(img)

def get_wrapped_text(text: str, font: PIL.ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

def print_image(sock, im):
    if im.width > printerWidth:
        # Scale down proportionately
        height = int(im.height * (printerWidth / im.width))
        im = im.resize((printerWidth, height))
        
    if im.width < printerWidth:
        # Pad with white pixels
        padded_image = PIL.Image.new("1", (printerWidth, im.height), 1)
        padded_image.paste(im)
        im = padded_image
        
    im = im.rotate(180)  # Adjust orientation
    
    # Convert to 1-bit
    if im.mode != '1':
        im = im.convert('1')
        
    # Ensure width is a multiple of 8
    if im.size[0] % 8:
        im2 = PIL.Image.new('1', (im.size[0] + 8 - im.size[0] % 8, im.size[1]), 'white')
        im2.paste(im, (0, 0))
        im = im2
        
    # Invert image for compatibility
    im = PIL.ImageOps.invert(im.convert('L')).convert('1')

    # Prepare data buffer
    width_bytes = im.size[0] // 8
    height = im.size[1]
    buf = b''.join((
        b'\x1d\x76\x30\x00', 
        struct.pack('<HH', width_bytes, height), 
        im.tobytes()
    ))
    
    initialize_printer(sock)  
    sleep(0.5)    
    send_start_print_sequence(sock)
    sleep(0.5)
    sock.send(buf)
    sleep(0.5)
    send_end_print_sequence(sock)
    sleep(0.5)

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

# FILENAME: img_processing.py DO NOT REMOVE COMMENT

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageChops
import PIL.ImageOps
import struct
from time import sleep
from printer import initialize_printer, send_start_print_sequence, send_end_print_sequence

printerWidth = 384

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

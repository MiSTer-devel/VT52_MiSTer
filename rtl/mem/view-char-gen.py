import numpy as np
from PIL import Image, ImageDraw

# VT52 Character ROM data (copied from the C# definition)
char_gen = [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x30, 0x40, 0x41, 0x31, 0x07, 0x09, 0x07,
    0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f,
    0x00, 0x21, 0x61, 0x22, 0x22, 0x74, 0x04, 0x08,
    0x00, 0x71, 0x09, 0x32, 0x0a, 0x74, 0x04, 0x08,
    0x00, 0x79, 0x41, 0x72, 0x0a, 0x74, 0x04, 0x08,
    0x00, 0x79, 0x09, 0x12, 0x22, 0x44, 0x04, 0x08,
    0x00, 0x18, 0x24, 0x18, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x08, 0x08, 0x7f, 0x08, 0x08, 0x7f,
    0x00, 0x00, 0x04, 0x02, 0x7f, 0x02, 0x04, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x49,
    0x00, 0x00, 0x08, 0x00, 0x7f, 0x00, 0x08, 0x00,
    0x00, 0x08, 0x08, 0x49, 0x2a, 0x1c, 0x08, 0x00,
    0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x7f, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7f, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7f,
    0x00, 0x00, 0x00, 0x30, 0x48, 0x48, 0x48, 0x30,
    0x00, 0x00, 0x00, 0x20, 0x60, 0x20, 0x20, 0x70,
    0x00, 0x00, 0x00, 0x70, 0x08, 0x30, 0x40, 0x78,
    0x00, 0x00, 0x00, 0x70, 0x08, 0x30, 0x08, 0x70,
    0x00, 0x00, 0x00, 0x10, 0x30, 0x50, 0x78, 0x10,
    0x00, 0x00, 0x00, 0x78, 0x40, 0x70, 0x08, 0x70,
    0x00, 0x00, 0x00, 0x38, 0x40, 0x70, 0x48, 0x30,
    0x00, 0x00, 0x00, 0x78, 0x08, 0x10, 0x20, 0x40,
    0x00, 0x00, 0x00, 0x30, 0x48, 0x30, 0x48, 0x30,
    0x00, 0x00, 0x00, 0x30, 0x48, 0x38, 0x08, 0x70,
    0x00, 0x3f, 0x7a, 0x7a, 0x3a, 0x0a, 0x0a, 0x0a,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x08,
    0x00, 0x14, 0x14, 0x14, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x14, 0x14, 0x7f, 0x14, 0x7f, 0x14, 0x14,
    0x00, 0x08, 0x3e, 0x48, 0x3e, 0x09, 0x3e, 0x08,
    0x00, 0x61, 0x62, 0x04, 0x08, 0x10, 0x23, 0x43,
    0x00, 0x1c, 0x22, 0x14, 0x08, 0x15, 0x22, 0x1d,
    0x00, 0x0c, 0x08, 0x10, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x04, 0x08, 0x10, 0x10, 0x10, 0x08, 0x04,
    0x00, 0x10, 0x08, 0x04, 0x04, 0x04, 0x08, 0x10,
    0x00, 0x08, 0x49, 0x2a, 0x1c, 0x2a, 0x49, 0x08,
    0x00, 0x00, 0x08, 0x08, 0x7f, 0x08, 0x08, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x10, 0x20,
    0x00, 0x00, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18,
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x00, 0x1c, 0x22, 0x45, 0x49, 0x51, 0x22, 0x1c,
    0x00, 0x08, 0x18, 0x28, 0x08, 0x08, 0x08, 0x3e,
    0x00, 0x3c, 0x42, 0x01, 0x0e, 0x30, 0x40, 0x7f,
    0x00, 0x7f, 0x02, 0x04, 0x0e, 0x01, 0x41, 0x3e,
    0x00, 0x04, 0x0c, 0x14, 0x24, 0x7f, 0x04, 0x04,
    0x00, 0x7f, 0x40, 0x5e, 0x61, 0x01, 0x41, 0x3e,
    0x00, 0x1e, 0x21, 0x40, 0x5e, 0x61, 0x21, 0x1e,
    0x00, 0x7f, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20,
    0x00, 0x3e, 0x41, 0x41, 0x3e, 0x41, 0x41, 0x3e,
    0x00, 0x3c, 0x42, 0x43, 0x3d, 0x01, 0x42, 0x3c,
    0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18,
    0x00, 0x00, 0x18, 0x18, 0x00, 0x18, 0x10, 0x20,
    0x00, 0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02,
    0x00, 0x00, 0x00, 0x7f, 0x00, 0x7f, 0x00, 0x00,
    0x00, 0x20, 0x10, 0x08, 0x04, 0x08, 0x10, 0x20,
    0x00, 0x3e, 0x41, 0x01, 0x0e, 0x08, 0x00, 0x08,
    0x00, 0x3e, 0x41, 0x45, 0x49, 0x4e, 0x40, 0x3e,
    0x00, 0x08, 0x14, 0x22, 0x41, 0x7f, 0x41, 0x41,
    0x00, 0x7e, 0x21, 0x21, 0x3e, 0x21, 0x21, 0x7e,
    0x00, 0x1e, 0x21, 0x40, 0x40, 0x40, 0x21, 0x1e,
    0x00, 0x7e, 0x21, 0x21, 0x21, 0x21, 0x21, 0x7e,
    0x00, 0x7f, 0x40, 0x40, 0x78, 0x40, 0x40, 0x7f,
    0x00, 0x7f, 0x40, 0x40, 0x78, 0x40, 0x40, 0x40,
    0x00, 0x3e, 0x41, 0x40, 0x47, 0x41, 0x41, 0x3e,
    0x00, 0x41, 0x41, 0x41, 0x7f, 0x41, 0x41, 0x41,
    0x00, 0x3e, 0x08, 0x08, 0x08, 0x08, 0x08, 0x3e,
    0x00, 0x01, 0x01, 0x01, 0x01, 0x01, 0x41, 0x3e,
    0x00, 0x41, 0x46, 0x58, 0x60, 0x58, 0x46, 0x41,
    0x00, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7f,
    0x00, 0x41, 0x63, 0x55, 0x49, 0x41, 0x41, 0x41,
    0x00, 0x41, 0x61, 0x51, 0x49, 0x45, 0x43, 0x41,
    0x00, 0x3e, 0x41, 0x41, 0x41, 0x41, 0x41, 0x3e,
    0x00, 0x7e, 0x41, 0x41, 0x7e, 0x40, 0x40, 0x40,
    0x00, 0x3e, 0x41, 0x41, 0x41, 0x45, 0x42, 0x3d,
    0x00, 0x7e, 0x41, 0x41, 0x7e, 0x44, 0x42, 0x41,
    0x00, 0x3e, 0x41, 0x40, 0x3e, 0x01, 0x41, 0x3e,
    0x00, 0x7f, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
    0x00, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x3e,
    0x00, 0x41, 0x41, 0x22, 0x22, 0x14, 0x14, 0x08,
    0x00, 0x41, 0x41, 0x41, 0x49, 0x49, 0x55, 0x22,
    0x00, 0x41, 0x22, 0x14, 0x08, 0x14, 0x22, 0x41,
    0x00, 0x41, 0x22, 0x14, 0x08, 0x08, 0x08, 0x08,
    0x00, 0x7f, 0x02, 0x04, 0x08, 0x10, 0x20, 0x7f,
    0x00, 0x3c, 0x30, 0x30, 0x30, 0x30, 0x30, 0x3c,
    0x00, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01,
    0x00, 0x1e, 0x06, 0x06, 0x06, 0x06, 0x06, 0x1e,
    0x00, 0x08, 0x14, 0x22, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7f,
    0x00, 0x18, 0x08, 0x04, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x3e, 0x01, 0x3f, 0x41, 0x3f,
    0x00, 0x40, 0x40, 0x5e, 0x61, 0x41, 0x61, 0x5e,
    0x00, 0x00, 0x00, 0x3e, 0x41, 0x40, 0x40, 0x3f,
    0x00, 0x01, 0x01, 0x3d, 0x43, 0x41, 0x43, 0x3d,
    0x00, 0x00, 0x00, 0x3c, 0x42, 0x7f, 0x40, 0x3e,
    0x00, 0x0e, 0x11, 0x7c, 0x10, 0x10, 0x10, 0x10,
    0x00, 0x00, 0x00, 0x1d, 0x22, 0x1e, 0x42, 0x3c,
    0x00, 0x40, 0x40, 0x7e, 0x41, 0x41, 0x41, 0x41,
    0x00, 0x08, 0x00, 0x18, 0x08, 0x08, 0x08, 0x3e,
    0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x41, 0x3e,
    0x00, 0x40, 0x40, 0x44, 0x48, 0x50, 0x44, 0x41,
    0x00, 0x18, 0x08, 0x08, 0x08, 0x08, 0x08, 0x1c,
    0x00, 0x00, 0x00, 0x76, 0x49, 0x49, 0x49, 0x49,
    0x00, 0x00, 0x00, 0x5e, 0x61, 0x41, 0x41, 0x41,
    0x00, 0x00, 0x00, 0x3e, 0x41, 0x41, 0x41, 0x3e,
    0x00, 0x00, 0x00, 0x5e, 0x61, 0x7e, 0x40, 0x40,
    0x00, 0x00, 0x00, 0x3d, 0x43, 0x3f, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x4e, 0x31, 0x20, 0x20, 0x20,
    0x00, 0x00, 0x00, 0x3e, 0x40, 0x3e, 0x01, 0x7e,
    0x00, 0x10, 0x10, 0x7c, 0x10, 0x10, 0x12, 0x0c,
    0x00, 0x00, 0x00, 0x42, 0x42, 0x42, 0x42, 0x3d,
    0x00, 0x00, 0x00, 0x41, 0x41, 0x22, 0x14, 0x08,
    0x00, 0x00, 0x00, 0x41, 0x41, 0x49, 0x55, 0x22,
    0x00, 0x00, 0x00, 0x42, 0x24, 0x18, 0x24, 0x42,
    0x00, 0x00, 0x00, 0x41, 0x22, 0x14, 0x08, 0x70,
    0x00, 0x00, 0x00, 0x7f, 0x02, 0x1c, 0x20, 0x7f,
    0x00, 0x07, 0x08, 0x08, 0x70, 0x08, 0x08, 0x07,
    0x00, 0x08, 0x08, 0x08, 0x00, 0x08, 0x08, 0x08,
    0x00, 0x70, 0x08, 0x08, 0x07, 0x08, 0x08, 0x70,
    0x00, 0x11, 0x2a, 0x44, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]

def create_character_bitmap(char_index, scale=3):
    """Create a bitmap for a single character."""
    char_width = 7  # 7 bits per byte
    char_height = 8  # 8 bytes per character
    base_addr = char_index * 8
    
    # Create a new image with white background
    img = Image.new('RGB', (char_width * scale, char_height * scale), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw each pixel
    for y in range(char_height):
        byte = char_gen[base_addr + y]
        for x in range(char_width):
            bit = (byte >> (6 - x)) & 1  # MSB first
            if bit:
                draw.rectangle([
                    x * scale, y * scale,
                    (x + 1) * scale - 1, (y + 1) * scale - 1
                ], fill='black')
    
    return img

def create_character_set_image(chars_per_row=16, scale=3):
    """Create an image containing all characters in the ROM."""
    char_width = 7  # 7 bits per byte
    char_height = 8  # 8 bytes per character
    total_chars = len(char_gen) // 8
    
    # Calculate rows needed
    rows = (total_chars + chars_per_row - 1) // chars_per_row
    
    # Create the full image with white background
    spacing = 2  # Pixels between characters (will be scaled)
    img_width = (char_width * chars_per_row + spacing * (chars_per_row - 1)) * scale
    img_height = (char_height * rows + spacing * (rows - 1)) * scale
    
    full_img = Image.new('RGB', (img_width, img_height), 'white')
    
    # Place each character in the image
    for char_idx in range(total_chars):
        row = char_idx // chars_per_row
        col = char_idx % chars_per_row
        
        char_img = create_character_bitmap(char_idx, scale)
        
        # Calculate position
        x = col * (char_width + spacing) * scale
        y = row * (char_height + spacing) * scale
        
        full_img.paste(char_img, (x, y))
    
    return full_img

def create_labeled_character_set():
    """Create character set image with labels."""
    # Create the base character set image
    scale = 3
    chars_per_row = 16
    char_img = create_character_set_image(chars_per_row, scale)
    
    # Create a new image with space for labels
    label_height = 20
    full_img = Image.new('RGB', 
                        (char_img.width, char_img.height + label_height), 
                        'white')
    draw = ImageDraw.Draw(full_img)
    
    # Paste the character set image
    full_img.paste(char_img, (0, label_height))
    
    # Add index labels
    char_width = (7 + 2) * scale  # character width + spacing
    for i in range(16):
        x = i * char_width + (char_width // 2) - 10
        draw.text((x, 2), f"{i:X}", fill='black')
    
    # Add row labels
    total_chars = len(char_gen) // 8
    rows = (total_chars + chars_per_row - 1) // chars_per_row
    for row in range(rows):
        y = row * (8 + 2) * scale + label_height - 10
        draw.text((0, y), f"{row * 16:02X}", fill='black')
    
    return full_img

if __name__ == "__main__":
    # Create and save the character set image
    img = create_labeled_character_set()
    img.save('vt52_charset.png')
    img.show()  # Display the image
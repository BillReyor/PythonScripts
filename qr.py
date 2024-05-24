#Install 
#pip install 'qrcode[pil]'
#pip install pillow

import qrcode
from PIL import Image, ImageDraw

def generate_qr_code_with_logo(url, file_path, logo_path, logo_size=(100, 100)):
    """
    Generate a QR code with a centered logo.

    Parameters:
    url (str): The URL to encode in the QR code.
    file_path (str): The file path to save the generated QR code image.
    logo_path (str): The file path of the logo image.
    logo_size (tuple): The size of the logo to be placed in the center of the QR code.

    Returns:
    None
    """
    # Create a QR Code instance with high error correction
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction allows for larger logos
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )

    # Add data to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code instance
    img = qr.make_image(fill='black', back_color='white').convert('RGB')

    # Open the logo image
    logo = Image.open(logo_path)

    # Resize the logo with high-quality resampling
    logo = logo.resize(logo_size, resample=Image.LANCZOS)

    # Calculate the position for the logo to be centered
    img_w, img_h = img.size  # Dimensions of the QR code image
    logo_w, logo_h = logo.size  # Dimensions of the logo image
    pos = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)  # Position to paste the logo

    # Create a white rectangle to place the logo on
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [(pos[0], pos[1]), (pos[0] + logo_w, pos[1] + logo_h)], 
        fill="white"
    )

    # Paste the logo image onto the QR code
    if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
        logo = logo.convert('RGBA')  # Ensure logo has an alpha channel for transparency
        img.paste(logo, pos, logo)  # Paste with transparency mask
    else:
        img.paste(logo, pos)  # Paste without transparency mask

    # Save the final image as a PNG file
    img.save(file_path)

# URL to encode in the QR code
url = 'https://github.com/tweag/ms-reactor-workshop'
# File path to save the generated QR code image
file_path = 'qrcode_with_larger_logo.png'
# File path of the logo image
logo_path = 'modus_logo.png'  # Replace with the path to your logo file

# Generate the QR code with the logo
generate_qr_code_with_logo(url, file_path, logo_path)

print(f"QR code with logo generated and saved as {file_path}")

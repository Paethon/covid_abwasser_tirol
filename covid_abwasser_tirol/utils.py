import os
import re
import subprocess
from io import BytesIO

import easyocr
import numpy as np
from mastodon import Mastodon
from PIL import Image


class ScreenshotError(Exception):
    """Exception raised when the screenshot fails."""

    pass


def take_shot(url: str, browser: str, selectors: str, width: int):
    """Take a screenshot of the given url and options using the shot-scraper CLI and return it as a PIL image."""
    # Create the command
    cmd = f"shot-scraper --width {width} -s {selectors} {url} --output tmp.png -b {browser}"
    # Run the command in the command line syncronously
    subprocess.run(cmd, shell=True)
    # Check if the file exists and raise an error if it doesn't
    if not os.path.exists("tmp.png"):
        raise ScreenshotError("Screenshot failed.")
    # Read the image
    with open("tmp.png", "rb") as f:
        img = Image.open(BytesIO(f.read()))
    # Remove the temporary file
    os.remove("tmp.png")

    return img


def get_text_from_image(image):
    """Get the text from the given image using easyocr."""
    reader = easyocr.Reader(lang_list=["de"])
    result = reader.readtext(image=np.array(image), low_text=0.1)
    return ". ".join([r[1] for r in result])


def extract_date_from_text(text):
    """Extracts the date from the given text."""
    # Regex that matches one or two digits, an arbitrary amount of dots and spaces, an arbitraty amount of letters an arbitrary amount of spaces and four digits
    regex = r"(\d{1,2})[\s\.]*?([a-zA-Z]+).*?(\d{4})"
    # Match the regex
    match = re.search(regex, text)
    if match is None:
        return None
    # Extract the day, month, year (capture group 1, 2, 3)
    day, month, year = match.groups()
    # Return the date as a string
    return f"{day}. {month} {year}"


def calc_pixel_difference(img1: Image.Image, img2: Image.Image):
    """Calculate the difference between two images in pixels."""
    # Check if the images have the same size
    if img1.size != img2.size:
        raise ValueError("Images must have the same size.")

    # Calculate the difference
    diff = np.sum(np.array(img1) - np.array(img2))

    return diff


def post_image(*, image, description, mastodon):
    """Post the given image to the mastodon instance and return the media id."""
    # Temporarily save the image as png and post it to mastodon
    image.save("mastodon_tmp.png")
    media_result = mastodon.media_post("mastodon_tmp.png", description=description)
    os.remove("mastodon_tmp.png")

    return media_result["id"]


def post_to_mastodon(message, image=None, description=""):
    # Log in
    mastodon = Mastodon(access_token="pytooter_usercred.secret")
    if image:
        media_id = post_image(image=image, description=description, mastodon=mastodon)
        mastodon.status_post(message, language="de", media_ids=[media_id])

from PIL import Image
from io import BytesIO
import subprocess
import os
import numpy as np


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


def calc_pixel_difference(img1: Image, img2: Image):
    """Calculate the difference between two images in pixels."""
    # Check if the images have the same size
    if img1.size != img2.size:
        raise ValueError("Images must have the same size.")

    # Calculate the difference
    diff = np.sum(np.array(img1) - np.array(img2))

    return diff

from covid_abwasser_tirol import utils
from PIL import Image
import datetime
import os
import sys

new_graph_threshold = 5  # Number of pixels that have to be different to consider the graph new
screenshot_path = "/home/paethon/git/covid_abwasser_tirol/screenshots/"


def get_shot():
    img = utils.take_shot(
        url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
        width=2048,
        browser="chromium",
        selectors="div.article-padding",
    )
    return img


def toot(img):
    # If the graph is new, save the screenshot as the new previous screenshot and post it to Mastodon
    img.save(os.path.join(screenshot_path, "previous_screenshot.png"))
    # Post the image to mastodon
    msg = """
    Aktuelle fiktive Ausscheider von SARS-CoV-2 und aktiv positive Personen in Tirol.
    Daten von https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/
    #tirol #covid19 #abwasser #monitoring
    """
    utils.post_to_mastodon(
        message=msg,
        image=img,
        description="Grafik welche den zeitlichen Verlauf der fiktiven Ausscheider von SARS-CoV-2 und aktiven positiven Personen in Tirol zeigt.",
    )


if __name__ == "__main__":
    # If no previous screenshot exists, create the screenshot directory, take a shot, post is and exit
    if not os.path.exists(os.path.join(screenshot_path, "previous_screenshot.png")):
        os.makedirs(screenshot_path)
        img = get_shot()
        img.save(os.path.join(screenshot_path, "previous_screenshot.png"))
        print("No previous screenshot found. Created one and directly posted it.")
        toot(img)
        sys.exit(0)

    # Load previous screenshot for comparison
    previous_screenshot = Image.open(os.path.join(screenshot_path, "previous_screenshot.png"))
    # Get screenshot of the current graph
    img = get_shot()
    # Get the bottom 20 pixels of both screenshots. This is where the date is displayed and we only want to compare the date
    # Sometimes the graph is updated slightly without the date changing and we don't want to flood the timeline
    previous_screenshot_bottom = previous_screenshot.crop(
        (0, previous_screenshot.height - 20, previous_screenshot.width, previous_screenshot.height)
    )
    img_bottom = img.crop((0, img.height - 20, img.width, img.height))
    # Compare the two screenshot bottoms
    diff = utils.calc_pixel_difference(previous_screenshot_bottom, img_bottom)
    if diff < new_graph_threshold:
        print(f"Graph is the same as before. Difference: {diff}")
        sys.exit(0)
    # Save the previous screenshot with the current date
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    previous_screenshot.save(os.path.join(screenshot_path, f"{timestamp}.png"))
    print(f"Graph is probably different. Difference: {diff}")
    toot(img)

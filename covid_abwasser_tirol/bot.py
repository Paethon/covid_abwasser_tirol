from covid_abwasser_tirol import utils
from PIL import Image
import datetime
import os
import sys
import json

new_graph_threshold = 5  # Number of pixels that have to be different to consider the graph new
date_portion_size = 25  # The bottom part of the screenshot contains the date (in pixels)
screenshot_path = "/home/paethon/git/covid_abwasser_tirol/screenshots/"


def get_shot():
    img = utils.take_shot(
        url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
        width=2048,
        browser="chromium",
        selectors="div.article-padding",
    )
    return img


def get_bottom(img):
    img_bottom = img.crop((0, img.height - date_portion_size, img.width, img.height))
    return img_bottom


def get_date(img_bottom):
    txt = utils.get_text_from_image(img_bottom)
    date = utils.extract_date_from_text(txt)
    return date


def save_dict(d, path):
    with open(path, "w") as f:
        json.dump(d, f)


def load_dict(path):
    with open(path, "r") as f:
        d = json.load(f)
    return d


def toot(img):
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
    # Check if --test_mode is passed
    test_mode = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test_mode":
            test_mode = True

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Take the screenshot, crop the bottom part and extract the date
    img = get_shot()
    img_bottom = get_bottom(img)
    date = get_date(img_bottom)
    assert date is not None, "Could not extract date from image"

    # If no previous screenshot was taken, create the screenshot directory if necessary, take a shot, post is and exit
    if not os.path.exists(os.path.join(screenshot_path, "state_dict.json")):
        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)

        img.save(os.path.join(screenshot_path, f"{timestamp}.png"))

        state_dict = {"previous_date": date}

        print("No previous screenshot found. Created one and directly posted it.")
        if not test_mode:
            save_dict(state_dict, os.path.join(screenshot_path, "state_dict.json"))
            toot(img)
        sys.exit(0)

    state_dict = load_dict(os.path.join(screenshot_path, "state_dict.json"))
    # Compare the new date and the old date
    old_date = state_dict["previous_date"]
    print(f"Old date: {old_date}, new date: {date}")

    # If the date has changed, save the new date, save the screenshot and post it
    if date != old_date:
        state_dict["previous_date"] = date

        print("Date has changed. Posting new toot.")
        if not test_mode:
            toot(img)
            save_dict(state_dict, os.path.join(screenshot_path, "state_dict.json"))
            img.save(os.path.join(screenshot_path, f"{timestamp}.png"))
    else:
        print("Date has not changed. Toot not posted.")

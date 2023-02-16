from covid_abwasser_tirol.utils import take_shot, ScreenshotError, calc_pixel_difference
from PIL import Image
import pytest


def test_take_shot():
    img = take_shot(
        url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
        width=2048,
        browser="chromium",
        selectors="div.article-padding",
    )
    assert isinstance(img, Image.Image)


def test_wrong_selectors_should_raise():
    with pytest.raises(ScreenshotError):
        take_shot(
            url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
            width=2048,
            browser="chromium",
            selectors="blablalba",
        )


def test_image_difference():
    # Take two screenshots
    img1 = take_shot(
        url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
        width=2048,
        browser="chromium",
        selectors="div.article-padding",
    )
    img2 = take_shot(
        url="https://www.tirol.gv.at/umwelt/wasserwirtschaft/abwasser-monitoring-tirol/",
        width=2048,
        browser="chromium",
        selectors="div.article-padding",
    )

    assert calc_pixel_difference(img1, img2) == 0

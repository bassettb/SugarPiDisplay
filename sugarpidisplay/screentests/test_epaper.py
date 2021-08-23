from sugarpidisplay.trend import Trend
from sugarpidisplay.utils import Reading
from sugarpidisplay.config_utils import Cfg, loadConfigDefaults
from sugarpidisplay.epd_dev import EPD_Dev
from sugarpidisplay.epaper_display import EpaperDisplay
from datetime import datetime, timezone



def test_orientations():
    epd = EPD_Dev()
    config = loadConfigDefaults()
    reading = Reading(datetime.now(timezone.utc), 120, Trend.DoubleUp)

    config[Cfg.orientation] = 0
    glucoseDisplay = EpaperDisplay(None, config, epd)
    glucoseDisplay.open()
    glucoseDisplay.clear()
    glucoseDisplay.update([reading])


    config[Cfg.orientation] = 270
    glucoseDisplay = EpaperDisplay(None, config, epd)
    glucoseDisplay.open()
    glucoseDisplay.clear()
    glucoseDisplay.update([reading])

    assert True

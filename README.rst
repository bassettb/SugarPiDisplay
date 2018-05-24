SugarPiDisplay
##############

Display your CGM data on a small LCD character display anywhere in your home or office.
Runs on a $10 Raspberry Pi.

.. image:: https://raw.githubusercontent.com/bassettb/SugarPiDisplay/master/docs/image1.jpg
    :alt: Photo of SugarPiDisplay

Features
--------

- Connects to either Dexcom Share or Nightscout.
- Shows latest glucose value, trend arrow, minutes since last reading
- Parts can be purchased for under $50
- Step-by-step instructions for setting up the Raspberry Pi (coming soon)
- Easy web interface for configuring access to your Dexcom or Nightscout data.


Recommended Setup
-----------------

- Raspberry Pi Zero W with soldered pin headers
- 2x16 LCD Character display with i2c port expander (backpack board)
- Wiring harness with 4 wires
- 4GB micro SDCard

Depending on your display location, you might also want:

- Case for the Pi Zero W
- Stand for the LCD display (Adafruit sells a great acrylic stand)


Supported I²C Port Expanders
----------------------------
- PCF8574


Web Interface
-------------
Once the Raspberry Pi Zero W is on your wifi network and SugarPiDisplay is running, it will display its IP address on the LCD display during bootup.  Put this IP into your browser, add ":8080" on the end, and you will get the configuration page seen below.

.. image:: https://raw.githubusercontent.com/bassettb/SugarPiDisplay/master/docs/ConfigScreenshot1.jpg
    :alt: Photo of Config screen



License
=======

This code is licensed under the MIT license, see the `LICENSE file
<https://github.com/bassettb/SugarPiDisplay/blob/master/LICENSE>`_ or `tldrlegal
<http://www.tldrlegal.com/license/mit-license>`_ for more information.

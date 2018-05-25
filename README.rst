SugarPiDisplay
##############

Display your CGM data on a mini LCD display anywhere in your home or office.
Runs on a $10 Raspberry Pi.

.. image:: https://raw.githubusercontent.com/bassettb/SugarPiDisplay/master/docs/image1.jpg
    :alt: Photo of SugarPiDisplay

Features
--------

- Connects to either Dexcom Share or Nightscout.
- Shows latest glucose value, trend arrow, minutes since last reading
- Parts can be purchased for under $50
- Step-by-step instructions for setting up the Raspberry Pi
- Easy web interface for configuring access to your Dexcom or Nightscout data.


Recommended Hardware
--------------------

- Raspberry Pi Zero W with soldered pin headers
- 2x16 LCD Character display with i2c port expander (backpack board, currently only supports the PCF8574 chip)
- Wiring harness with 4 wires
- 4GB (or larger) micro SDCard

Depending on your display location, you might also want:

- Case for the Pi Zero W
- Stand for the LCD display (Adafruit sells a great acrylic stand)



Web Interface
-------------
Once the Raspberry Pi Zero W is on your wifi network and SugarPiDisplay is running, the IP address will be displayed on the LCD during bootup.  Type this IP into your browser, add ":8080" on the end, and you will get the configuration page seen below.

.. image:: https://raw.githubusercontent.com/bassettb/SugarPiDisplay/master/docs/ConfigScreenshot1.png
    :alt: Photo of Config screen

Instructions
------------
- `Hardware <http://https://github.com/bassettb/SugarPiDisplay/blob/master/docs/hardware_setup.rst>`_
- `Software <http://https://github.com/bassettb/SugarPiDisplay/master/docs/software_setup.rst>`_


License
=======

This code is licensed under the MIT license, see the `LICENSE file
<https://github.com/bassettb/SugarPiDisplay/blob/master/LICENSE>`_ or `tldrlegal
<http://www.tldrlegal.com/license/mit-license>`_ for more information.
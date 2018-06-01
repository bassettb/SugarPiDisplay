
Hardware
========

- Raspberry Pi Zero W with soldered pin headers.  
- 2x16 LCD Character display with i2c port expander (backpack board, currently only supports the PCF8574 chip)
- Wiring harness with 4 female-female wires (Pi and LCD will both have standard 0.1" pins)
- 4GB (or larger) microSD card

Depending on your display location, you might also want:

- Case for the Pi Zero W
- Stand for the LCD display (Adafruit sells a great acrylic stand)

Adapters
========

For setting up the Raspberry Pi, you will need a USB OTG cable for the keyboard and mini-HDMI cable.  Some Pi Zero W kits come with these cables or you might have them already.  

Screens
=======
The 2x16 character display is a very common part that is sold in multiple colors.  The base part has a 16 pin header, requires at least 10 wire connections, and requires extra circuitry for contrast control.  A more hobby-friendly version has an I2C backpack board soldered onto the back, providing a 4-pin connection and easy contrast control.


Wiring
======

Pin 1 is above the microSD card slot

.. image:: https://raw.githubusercontent.com/bassettb/SugarPiDisplay/master/docs/wiring-i2c.png
    :alt: Wiring

Thanks to the RPLCD project for the interface library and this wiring diagram.
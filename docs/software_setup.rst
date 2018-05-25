
Install Raspian OS
==================
Flash the microSD with Raspian-Stretch-Lite


Configuring Raspberry Pi
==================================
``sudo raspi-config``

- configure wifi
- enable ssh   # optional
- enable i2c

Installing Dependencies
=======================
``sudo apt-get update``

``sudo apt-get install python3-pip``

``sudo apt-get install python3-smbus``

``sudo apt-get install git``

``sudo pip3 install RPLCD``

``sudo pip3 install flask_wtf``


Installing SugarPiDisplay
=========================
``git clone https://github.com/bassettb/SugarPiDisplay.git``

``sudo chmod 755 SugarPiDisplay/install.sh``

``SugarPiDisplay/install.sh``


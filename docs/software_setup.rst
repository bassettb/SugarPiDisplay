
Install Raspian OS
==================
Flash the microSD with Raspian-Stretch-Lite


Configuring Raspberry Pi
==================================
``sudo raspi-config``

- configure wifi
- enable ssh   # optional
- enable i2c
- setup localization (the default GB keyboard layout will be a problem if your wifi password has any symbols)

Once Wifi and SSH are configured, you can reboot and connect to it using SSH for the rest of the setup. 

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

reboot the Pi and SugarPiDisplay should be running


Configuring SugarPiDisplay
==========================

- Once SugarPiDisplay is running, you can configure it using its web interface on port 8080.  It will display its IP address on startup.  Enter this IP into your browser with ":8080" on the end and you'll see the config screen.  From here you can pick Dexcom or Nightscout and enter in the necessary fields.   
- Nightscout token: If you will be getting your CGM data from nightscout, you'll have to set up a "user" in nightscout.  Under the Admin Tools screen, click the "Add new Subject" button.  Give it a name like SugarPi.  For role, use the "readable" role.  Click Save.  In the list of subjects, your new role will be listed with a generated access token (something like "sugarpi-8c8766b098a988f".  That token is entered under "Nightscout Access Token" in the SugarPiDisplay config.  Note: this requires Nightscout version 0.9 or later.

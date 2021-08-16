#!/bin/bash

cd $HOME/SugarPiDisplay
chmod 755 sugarpidisplay.sh
chmod 755 network-check.sh
chmod 755 network-check.cron

sudo cp -f network-check.cron /etc/cron.d/network-check

sudo cp -f sugarpidisplay.init /etc/init.d/sugarpidisplay
sudo chmod 755 /etc/init.d/sugarpidisplay
sudo update-rc.d sugarpidisplay defaults
sudo service sugarpidisplay start
sudo service sugarpidisplay status

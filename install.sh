#!/bin/bash

cd $HOME/SugarPiDisplay

sudo cp -f network-check.cron /etc/cron.d/network-check

sudo cp -f sugarpidisplay.init /etc/init.d/sugarpidisplay
sudo chmod 755 /etc/init.d/sugarpidisplay
sudo update-rc.d sugarpidisplay defaults
sudo service sugarpidisplay start
sudo service sugarpidisplay status

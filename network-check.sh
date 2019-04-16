#!/bin/bash

if ! (/sbin/ifconfig wlan0 | grep -q "inet ") ; then
    echo "$(date) Network connection down! Attempting reconnection." >> /home/pi/.sugarpidisplay/sugarpidisplay.log
    ip link set wlan0 down
    ip link set wlan0 up
fi

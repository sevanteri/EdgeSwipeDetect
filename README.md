EdgeSwipeDetect
===============

Edge swipe detector for my Lenovo X230T. Uses python-evdev.


Usage Example
=============

    #!/bin/sh

    ./EdgeSwipeDetect.py | while read line; do
        if [ "$line" = "left" ]; then
            /home/sevanteri/Copy/Workspace/python/pyqt5/tabletShortcuts/run.sh&
        elif [ "$line" = "tap_3" ]; then
            if [ `xsetwacom --get 'Wacom ISDv4 E6 Finger touch' Touch` == "off" ]; then
                xsetwacom --set 'Wacom ISDv4 E6 Finger touch' Touch on
            else
                xsetwacom --set 'Wacom ISDv4 E6 Finger touch' Touch off
            fi
        elif [ "$line" = "bottom" ]; then
            xdotool keydown alt key Tab keyup alt
        fi
    done


Todo
====

Check screen orientation
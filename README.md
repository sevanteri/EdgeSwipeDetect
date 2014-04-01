EdgeSwipeDetect
===============

Edge swipe detector for my Lenovo X230T. Uses python-evdev.


Examples
========

    sudo ./EdgeSwipeDetect.py | while read line; do
        if [ $line = "left" ]; then
            /home/sevanteri/Copy/Workspace/python/pyqt5/tabletShortcuts/run.sh&
        fi
    done


Todo
====

Get rid of the need for sudo.

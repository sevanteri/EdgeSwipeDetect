EdgeSwipeDetect
===============

Edge swipe detector for my Lenovo X230T. Uses python-evdev.


Examples
========

´´´bash
#!/bin/sh

sudo ./EdgeSwipeDetect.py | while read line; do
    if [ $line = "left" ]; then
        /home/sevanteri/Copy/Workspace/python/pyqt5/tabletShortcuts/run.sh&
    fi
done
```
#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import evdev
from evdev import ecodes
from evdev.device import InputDevice
from select import select


class EdgeSwipeDetect:
    def __init__(self, argv):
        self.dev = None
        self.running = False

        self.touching = 0

        self.last_x = -1
        self.last_y = -1

        self.max_x = -1
        self.max_y = -1

        self.handlingLeft = self.handlingRight = False
        self.handlingTop = self.handlingBottom = False

        print("getting device")
        de = None
        for d in evdev.list_devices():
            de = InputDevice(d)
            searchTerm = len(argv) > 1 and argv[1] or "finger"
            if de.name.lower().rfind(searchTerm) > 0:
                break
        self.dev = de

        print("device: ", self.dev)
        if self.dev:
            for cap in self.dev.capabilities()[ecodes.EV_ABS]:
                if cap[0] == ecodes.ABS_MT_POSITION_X:
                    self.max_x = cap[1].max
                elif cap[0] == ecodes.ABS_MT_POSITION_Y:
                    self.max_y = cap[1].max

            print("max x: ", self.max_x)
            print("max y: ", self.max_y)

    def run(self):
        if not self.dev:
            return

        self.running = True
        while self.running:
            r, w, x = select([self.dev.fd], [], [], 1)
            if r:
                if not self.running:
                    break
                for event in self.dev.read():
                    if event.code == ecodes.ABS_MT_POSITION_X:
                        self.handleXChange(event.value)
                    elif event.code == ecodes.ABS_MT_POSITION_Y:
                        self.handleYChange(event.value)

                    elif event.code == ecodes.BTN_TOUCH:
                        self.touching = event.value
                        if not self.touching:  # oh my
                            self.handlingLeft = self.handlingRight = False
                            self.handlingTop = self.handlingBottom = False

    def handleXChange(self, x):
        if x == 0:
            print("left")
            self.handlingLeft = True
        elif x == self.max_x:
            print("right")
            self.handlingRight = True

        if self.handlingLeft:
            self.handleLeftEdge(x)
        if self.handlingRight:
            self.handleRightEdge(x)

    def handleYChange(self, y):
        if y == 0:
            print("top")
            self.handlingTop = True
        elif y == self.max_y:
            print("bottom")
            self.handlingBottom = True

        if self.handlingTop:
            self.handleTopEdge(y)
        if self.handlingBottom:
            self.handleBottomEdge(y)

    def handleLeftEdge(self, x):
        print("l%d" % (x))

    def handleRightEdge(self, x):
        print("r%d" % (self.max_x - x))

    def handleTopEdge(self, y):
        print("t%d" % (y))

    def handleBottomEdge(self, y):
        print("b%d" % (self.max_y - y))


def main():
    return EdgeSwipeDetect(sys.argv).run()

if __name__ == '__main__':
    main()

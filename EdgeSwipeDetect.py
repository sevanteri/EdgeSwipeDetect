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
        self.counter = 0

        self.margin = 2
        self.touching = 0
        self.handling = ""

        self.value = -1
        self.last_value = -1

        self.max_x = -1
        self.max_y = -1

        for d in evdev.list_devices():
            de = InputDevice(d)
            searchTerm = len(argv) > 1 and argv[1] or "finger"
            if de.name.lower().rfind(searchTerm) > 0:
                self.dev = de
                break

        print("device: ", self.dev, file=sys.stderr)
        if self.dev:
            for cap in self.dev.capabilities()[ecodes.EV_ABS]:
                if cap[0] == ecodes.ABS_MT_POSITION_X:
                    self.max_x = cap[1].max
                elif cap[0] == ecodes.ABS_MT_POSITION_Y:
                    self.max_y = cap[1].max

            print("max x: ", self.max_x, file=sys.stderr)
            print("max y: ", self.max_y, file=sys.stderr)

    def run(self):
        if not self.dev:
            return

        self.running = True
        while self.running:
            r, w, x = select([self.dev.fd], [], [])
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
                        if self.handling and not self.touching:  # oh my
                            if self.value >= self.last_value \
                                and self.value > 10:
                                    print(self.handling)
                            # else:
                            #     print(self.handling, "canceled")

                            # print(self.handling, "end")
                            self.handling = ""
                            self.value = -1
                            self.last_value = -1

                    sys.stdout.flush()

    def handleXChange(self, x):
        if x <= self.margin and not self.handling:
            # print("left started")
            self.handling = "left"
        elif x >= self.max_x - self.margin and not self.handling:
            # print("right started")
            self.handling = "right"

        if self.handling == "left":
            self.handleLeftEdge(x)
        elif self.handling == "right":
            self.handleRightEdge(x)

        if abs(self.last_value - self.value) > 20:
            self.last_value = self.value

    def handleYChange(self, y):
        if y <= self.margin and not self.handling:
            # print("top started")
            self.handling = "top"
        elif y >= self.max_y - self.margin and not self.handling:
            # print("bottom started")
            self.handling = "bottom"

        if self.handling == "top":
            self.handleTopEdge(y)
        if self.handling == "bottom":
            self.handleBottomEdge(y)

        if abs(self.last_value - self.value) > 20:
            self.last_value = self.value

    def handleLeftEdge(self, x):
        self.value = x / self.max_x * 100
        # print("l%d" % (x / self.max_x * 100))

    def handleRightEdge(self, x):
        self.value = (self.max_x - x) / self.max_x * 100
        # print("r%d" % ((self.max_x - x) / self.max_x * 100))

    def handleTopEdge(self, y):
        self.value = y / self.max_y * 100
        # print("t%d" % (y / self.max_y * 100))

    def handleBottomEdge(self, y):
        self.value = (self.max_y - y) / self.max_y * 100
        # print("b%d" % ((self.max_y - y) / self.max_y * 100))


def main():
    return EdgeSwipeDetect(sys.argv).run()

if __name__ == '__main__':
    main()

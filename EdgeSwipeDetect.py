#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import evdev
from evdev import ecodes
from evdev.device import InputDevice
from select import select

from datetime import datetime


class EdgeSwipeDetect:
    def __init__(self, argv):
        self.dev = None
        self.running = False
        self.counter = 0
        self.last_tap = -1

        self.margin = 2
        self.touching = 0
        self.handling = ""

        self.value = -1
        self.last_value = -1

        self.min_x = self.min_y = self.max_x = self.max_y = self.min_xy = -1

        for d in evdev.list_devices():
            de = InputDevice(d)
            searchTerm = len(argv) > 1 and argv[1] or "finger"
            if de.name.lower().rfind(searchTerm.lower()) > 0:
                self.dev = de
                break

        print("device: ", self.dev, file=sys.stderr)
        if self.dev:
            for cap in self.dev.capabilities()[ecodes.EV_ABS]:
                if cap[0] == ecodes.ABS_MT_POSITION_X:
                    self.min_x = cap[1].min
                    self.max_x = cap[1].max
                elif cap[0] == ecodes.ABS_MT_POSITION_Y:
                    self.min_y = cap[1].min
                    self.max_y = cap[1].max

            self.min_xy = min(self.max_y - self.min_y, self.max_x - self.min_x)
            print("min x: ", self.min_x, file=sys.stderr)
            print("max x: ", self.max_x, file=sys.stderr)
            print("min y: ", self.min_y, file=sys.stderr)
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
                                and self.value > self.min_xy * 0.1:

                                    print(self.handling)
                            # else:
                            #     print(self.handling, "canceled")

                            # print(self.handling, "end")
                            self.handling = ""
                            self.value = -1
                            self.last_value = -1
                            self.dev.ungrab()

                        if not self.handling and not self.touching:
                            now = datetime.now().timestamp()
                            if now - self.last_tap > 0.25:
                                self.counter = 1
                            else:
                                self.counter += 1
                            self.last_tap = now

                            if self.counter == 3:
                                print("tap_3")
                                self.counter = 0

                    sys.stdout.flush()

    def handleXChange(self, x):
        if x <= self.min_x + self.margin and not self.handling:
            # print("left started")
            self.handling = "left"
            self.dev.grab()
        elif x >= self.max_x - self.margin and not self.handling:
            # print("right started")
            self.handling = "right"
            self.dev.grab()

        if self.handling == "left":
            self.handleLeftEdge(x)
        elif self.handling == "right":
            self.handleRightEdge(x)

        if abs(self.last_value - self.value) > self.min_xy * 0.2:
            self.last_value = self.value

    def handleYChange(self, y):
        if y <= self.min_y + self.margin and not self.handling:
            # print("top started")
            self.handling = "top"
            self.dev.grab()
        elif y >= self.max_y - self.margin and not self.handling:
            # print("bottom started")
            self.handling = "bottom"
            self.dev.grab()

        if self.handling == "top":
            self.handleTopEdge(y)
        if self.handling == "bottom":
            self.handleBottomEdge(y)

        if abs(self.last_value - self.value) > self.min_xy * 0.2:
            self.last_value = self.value

    def handleLeftEdge(self, x):
        self.value = x
        # print("l%d" % (x / self.max_x * 100))

    def handleRightEdge(self, x):
        self.value = (self.max_x - x)
        # print("r%d" % ((self.max_x - x) / self.max_x * 100))

    def handleTopEdge(self, y):
        self.value = y
        # print("t%d" % (y / self.max_y * 100))

    def handleBottomEdge(self, y):
        self.value = (self.max_y - y)
        # print("b%d" % ((self.max_y - y) / self.max_y * 100))


def main():
    return EdgeSwipeDetect(sys.argv).run()

if __name__ == '__main__':
    main()

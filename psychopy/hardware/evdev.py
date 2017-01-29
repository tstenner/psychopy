from __future__ import absolute_import

import evdev
import evdev.ecodes as ev
from time import time


def list_devices():
    for fn in evdev.list_devices():
        dev = evdev.InputDevice(fn)
        cap = dev.capabilities()
        if ev.EV_KEY in cap:
            yield dev


def _first_name(keyid):
    keyname = ev.keys[keyid]
    if isinstance(keyname, list):
        return keyname[0]
    return keyname


class EvdevDevice(object):
    """An evdev device, currently limited to anything with a button"""

    def __init__(self, device, exclusive=False):
        self._device = device
        if exclusive:
            self._grabbed = True
            self._device.grab()
        self.buttons = {_first_name(keyid): keyid for keyid in device.capabilites()[ev.EV_KEY]}
        self.names = {value: key for key,value in self.buttons.iteritems()}
        self.basetime = time()

    def clear(self):
        """Clears any previous events in the event queue and resets the base time"""
        self._get_events()
        self.basetime = time()

    def _get_events(self):
        try:
            events = list(self._device.read())
        except IOError: # queue is empty
            print('Looks like the device was idle since the last read')

    def get_events(self, type=ev.EV_KEY):
        for event in self._get_events():
            if event.type == type:
                yield event

    def get_first_btn_press(self):
        for event in self._get_events():
            if event.type == ev.EV_KEY and event.value == 1:
                event.reltime = event.timestampe() - self.basetime
                return event
        return None

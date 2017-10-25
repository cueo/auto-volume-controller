"""
Inspired: https://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/

Automatic volume controller for MacOS.
Handle the abnormal increase or decrease
"""

import pyaudio
import numpy as np
import applescript

from data import *


class VolumeController:
    def __init__(self, rate, chunk):
        self.rate = rate
        self.chunk = chunk

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.rate, input=True,
                                  frames_per_buffer=self.chunk)

        self.MAX = 1000
        self.DIFF = 200
        self.UNIT_INCR = self.DIFF / 20
        self.LOUD = 1500
        self.QUIET = 300
        self.HIGH_CONTROLLER = 70
        self.LOW_CONTROLLER = 20

        self.output_vol_str = applescript.AEType('ouvl')
        self.get_vol_cmd_str = 'get volume settings'
        self.set_vol_cmd_str = 'set volume output volume '

        self.HIGH = 1
        self.LOW = 2
        self.ABRUPT = 3

    def get_volume(self):
        """
        Get current volume of the system
        :return current volume of the system
        """
        return applescript.AppleScript(self.get_vol_cmd_str).run()[self.output_vol_str]

    def set_volume(self, val, op):
        """
        Increase or decrease the system volume based on the parameter passed
        :param val: raw value to calculate increment
        :param op: type of the set volume operation
        """
        print 'Operation:', op
        current_volume = self.get_volume()
        if op == self.ABRUPT:
            incr = val / self.UNIT_INCR
            new_volume = current_volume - incr
            print 'Current:', current_volume, 'New:', new_volume
            print val, incr

        elif op == self.HIGH:
            new_volume = current_volume - val / self.HIGH_CONTROLLER
            new_volume = new_volume if new_volume > 25 else 25

        elif op == self.LOW:
            new_volume = current_volume + val / self.LOW_CONTROLLER
            new_volume = new_volume if new_volume > 80 else 80

        else:
            new_volume = current_volume

        cmd = self.set_vol_cmd_str + str(new_volume)
        applescript.AppleScript(cmd).run()

    def calculate_peak(self):
        """
        Calculate rms value or something from the streaming audio through the microphone
        :return: calculated value
        """
        data = np.fromstring(self.stream.read(self.chunk), dtype=np.int16)
        peak = np.average(np.abs(data)) * 2
        return peak

    def control_volume(self):
        """
        Continuously check system volume for abrupt increase or decrease
        :return:
        """
        last_peak = self.MAX / 2  # last normalized peak value
        while True:  # go infinitely
            peak = self.calculate_peak()
            normalized_peak = int(50 * peak / self.MAX)  # normalized value of the peak

            # abrupt increase or decrease in volume
            diff = normalized_peak - last_peak
            last_peak = normalized_peak
            print 'level:', normalized_peak, '\t', 'diff:', diff
            if diff > self.DIFF:
                self.set_volume(diff, self.ABRUPT)

            # if volume is too high
            if peak > self.LOUD:
                self.set_volume(peak, self.HIGH)

            # if volume is too low
            if peak < self.LOUD:
                self.set_volume(peak, self.LOW)

            bars = '#' * normalized_peak
            print '%05d %s' % (peak, bars)


if __name__ == '__main__':
    vol = VolumeController(RATE, CHUNK)
    vol.control_volume()
    # while True:
    #     peak = vol.calculate_peak()
    #     print peak

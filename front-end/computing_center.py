import cv2 as cv
import threading as t
import copy
import time
from remote_zone import Remote_zone
from frames_buffer import Ring_buffer


class Computing_center:

    def __init__(self, buffer_size, original_buffer_size, ratio, names_file):
        self.original_buffer_size = original_buffer_size
        self.buffer_size = buffer_size
        self.ratio = ratio
        self.names_file = names_file
        self.zones = {}
        self.devices = []

        self.last_original_frames_buffers = {}
        self.last_rendered_frames = {}

        self.original_frames_locks = {}


    def add_device(self, dev):
        self.devices.append(dev)

        for zone in self.last_rendered_frames.values():
            zone[dev] = None

        for zone in self.zones.values():
            zone.add_device(dev)

        self.last_original_frames_buffers[dev] = Ring_buffer(self.original_buffer_size)


    def get_devices(self):
        self.devices.sort()
        return self.devices


    def get_zones(self):
        return self.zones.keys()


    def add_zone(self, name, zone):
        self.zones[name] = Remote_zone(name, zone, self.buffer_size, self.ratio, self.names_file)
        self.last_rendered_frames[zone] = {}
    
    
    def get_rendered_frame(self, zone, device):
        while True:

            frame = self.zones[zone].get_last_rendered_frame(device)
            
            if frame is None:
                continue

            success, encoded_img = cv.imencode(".jpg", frame)

            if not success:
                continue

            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' 
            + bytearray(encoded_img) + b'\r\n')


    def dispatch_frame(self, frame, device):
        self.last_original_frames_buffers[device].push_frame(frame)

        for zone in self.zones.values():
            zone.push_frame(frame, device)


    def get_original_frame(self, device):
        while True:

            frame = self.last_original_frames_buffers[device].pop_frame()

            if frame is None:
                continue
            
            success, encoded_img = cv.imencode(".jpg", frame)

            if not success:
                continue

            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' 
            + bytearray(encoded_img) + b'\r\n')

                    







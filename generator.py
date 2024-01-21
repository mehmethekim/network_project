import random
from packet import Packet
import threading
import time
SLEEP_MS = 1000.0
#There will be 4 packet generators that are working in parallel.
class PacketGenerator:
    def __init__(self, id,scheduler,packet_length=100, generation_rate=100, distribution_mean=3, distribution_std=1):
        self.packet_length = packet_length
        self.generation_rate = generation_rate
        self.distribution_mean = distribution_mean
        self.distribution_std = distribution_std
        self.tick = 0
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()
        self.id = id
        self.scheduler = scheduler
        self.packet_counter = 0
    def generate_packets(self):
        # Generate the number of packets from a Gaussian distribution
        num_packets = max(1, int(random.gauss(self.distribution_mean, self.distribution_std)))# minimum 1 packet is generated
        current_time_ms = int(time.time() * 1000)
        packets = []
        # Generate packets with a fixed size
        for _ in range(num_packets):
            packet = Packet(incoming_port=self.id, size=self.packet_length, arrival_time=current_time_ms,id = self.packet_counter )
            self.packet_counter += 1
            packets.append(packet)
            #print(packet)
        
        self.scheduler.enqueue_packets(packets,self.id)
        return packets
    
    def run(self):
        while not self.stop_event.is_set():
            print("Generating packets from:",self.id)
            packets = self.generate_packets()
            time.sleep(SLEEP_MS/1000.0)
    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
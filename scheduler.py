import threading
import time
from queue import Queue
from packet import Packet
from generator import PacketGenerator,SLEEP_MS
MEAN_PACKET_LENGTH = 100
MEAN_PACKET_COUNT = 10
class BaseScheduler:
    def __init__(self,num_of_input_ports=4,distribution_mean=MEAN_PACKET_COUNT,packet_length=MEAN_PACKET_LENGTH):
        self.num_of_input_ports = num_of_input_ports
        self.generators = []
        self.input_queues = []
        self.distribution_mean = distribution_mean
        self.packet_length = packet_length
        for i in range(num_of_input_ports):
            self.generators.append(PacketGenerator(id=i,scheduler=self,distribution_mean=self.distribution_mean,packet_length=self.packet_length))
            self.input_queues.append(Queue())
        self.output_queue = Queue()
        self.output_queue.empty()
        self.lock = threading.Lock()
        # Clear the queues at the beginning
        self.clear_queues()
    def clear_queues(self):
        with self.lock:
            for input_queue in self.input_queues:
                input_queue.queue.clear()
            self.output_queue.queue.clear()

    def enqueue_packets(self, packets,port_id):
        with self.lock:
            print("Incoming packets from:",port_id,"packet count:",len(packets),"queue size:",self.input_queues[port_id].qsize())
            for packet in packets:
                self.input_queues[port_id].put(packet)
            print("Queue size:",self.input_queues[port_id].qsize())
    def start_generators(self):
        for generator in self.generators:
            generator.start()
    def schedule(self):
        raise NotImplementedError("Subclasses must implement the schedule method")
    def serve_packets(self):
        raise NotImplementedError("Subclasses must implement the serve_packets method")
    def start_simulation(self):
        

        # Create a thread for the scheduler simulation
        scheduler_thread = threading.Thread(target=self.simulate)
        
        self.start_generators()
        try:
            # Start the scheduler thread
            scheduler_thread.start()

            # Wait for the scheduler thread to finish
            scheduler_thread.join()

        except KeyboardInterrupt:
            print("Ctrl-C detected. Stopping threads.")
            self.stop_generators()
    
    def simulate(self):
        while True:
            self.schedule()
            served_packets = self.serve_packets()
            print("-----Served packets:------")
            print(len(served_packets))
            print("--------------------------")
            print("Output queue size:",len(self.output_queue.queue))
            time.sleep(SLEEP_MS/1000.0)

    def stop_generators(self):
        for generator in self.generators:
            generator.stop()
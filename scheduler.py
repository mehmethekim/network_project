import threading
import time
from queue import Queue
from packet import Packet
from generator import PacketGenerator,SLEEP_MS
import matplotlib.pyplot as plt
import numpy as np
MEAN_PACKET_LENGTH = 100
MEAN_PACKET_COUNT = 10.0
class BaseScheduler:
    def __init__(self,name,num_of_input_ports=4,distribution_mean=MEAN_PACKET_COUNT,packet_length=MEAN_PACKET_LENGTH):
        self.num_of_input_ports = num_of_input_ports
        self.name = name
        self.generators = []
        self.input_queues = []
        self.network_load = 0.8
        self.latency_data = []  # List to store latency data
        self.queue_fairness_data = []  # List to store queue fairness data
        self.served_percentage_data = []  # List to store served percentage data
        self.network_load_list = []
        self.distribution_mean = distribution_mean
        self.packet_length = packet_length
        for i in range(num_of_input_ports):
            if i == 0:
                self.generators.append(PacketGenerator(id=i,scheduler=self,distribution_mean=self.distribution_mean+2,packet_length=self.packet_length))
            else:
                self.generators.append(PacketGenerator(id=i,scheduler=self,distribution_mean=self.distribution_mean,packet_length=self.packet_length))
            self.input_queues.append(Queue(1000))
        self.output_queue = Queue(1000)
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
        self.stop_generators()
    def simulate(self):
        time_tick = 0
        
        while time_tick<200:
            self.schedule()
            served_packets = self.serve_packets()
            print("-----Served packets:------")
            print(len(served_packets))
            print("--------------------------")
            print("Output queue size:",len(self.output_queue.queue))
            
            # Calculate latency and queue fairness
            
            current_time_ms = int(time.time() * 1000)
            for packet in served_packets:
                latency = (current_time_ms - packet.arrival_time) / 1000.0
                self.latency_data.append(latency)

            # Calculate and store queue fairness data
            queue_sizes = [self.input_queues[i].qsize() for i in range(self.num_of_input_ports)]
            queue_fairness = max(queue_sizes) / min(queue_sizes) if min(queue_sizes) > 0 else 1
            self.queue_fairness_data.append(queue_fairness)

            # Calculate and store served percentage data
            served_percentage = [0] * self.num_of_input_ports
            total_served = len(served_packets)
            for packet in served_packets:
                served_percentage[packet.incoming_port] += 1 / total_served * 100
            
            self.served_percentage_data.append(served_percentage)
            self.network_load_list.append(self.network_load)
            if time_tick %20 == 0:
                if self.network_load < 1.1:
                    self.network_load += 0.1
            time_tick += 1
            time.sleep(SLEEP_MS/1000.0)
    def stop_generators(self):
        for generator in self.generators:
            generator.stop()
    def plot_data(self):
        # Plot latency data
        plt.figure(figsize=(12, 6))
        plt.subplot(3 ,1, 1)
        plt.plot(self.latency_data, label='Latency')
        plt.title('Latency Over Time')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Latency (seconds)')
        plt.legend()

        # # Plot queue fairness data
        # plt.subplot(4, 1, 2)
        # plt.plot(self.queue_fairness_data, label='Queue Fairness')
        # plt.title('Queue Fairness Over Time')
        # plt.xlabel('Time (ticks)')
        # plt.ylabel('Queue Fairness')
        # plt.legend()

        # Plot served percentage data
        plt.subplot(3, 1, 2)
        for i in range(self.num_of_input_ports):
            plt.plot([percentage[i] for percentage in self.served_percentage_data], label=f'Port {i} Served Percentage')

        plt.title('Served Percentage Over Time')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Served Percentage')
        plt.legend()
        
        #Plot network load
        plt.subplot(3,1,3)
        plt.plot(self.network_load_list,label='Network Load')
        plt.title('Network Load Over Time')
        plt.xlabel('Time (ticks)')
        plt.ylabel('Network Load')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f"{self.name}plot.png")

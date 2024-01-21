from scheduler import BaseScheduler
import time
MIN_BYTE_SEND = 10
class FIFOScheduler(BaseScheduler):
    def __init__(self, num_of_input_ports=4):
        super().__init__(num_of_input_ports)
    
    def serve_packets(self):
        served_packets = []
        #There are 4 input ports. With packet length of 100 bytes and 10 packets per second approximately 4000 bytes will be served every second no served.
        #If quees are empty, break the loop.
        #Look at the output queue. In a while loop serve 10 bytes in a while loop.
        #If the packet is done, put it in the served_packets list. At most num_of_input_ports * distribution_mean*mean_packet_length bytes will be served.
        with self.lock:
            served_bytes = 0
            while served_bytes < self.num_of_input_ports *self.distribution_mean*self.packet_length:
                if self.output_queue.empty():
                    break
                packet = self.output_queue.get()#Get the packet from the output queue.
                if not packet.is_done():
                    packet.serve(MIN_BYTE_SEND)
                
                if packet.is_done():
                    packet.serve_time = int(time.time() * 1000)
                    served_packets.append(packet)
                else:
                    self.output_queue.put(packet)
                served_bytes += MIN_BYTE_SEND
        return served_packets
    def schedule(self):
        # Iterate over input queues and find the packet with the lowest arrival time
        #Scheduling is in a loop. Because there we are serving at most 4000 bytes per second,
        #we need to schedule 4000 bytes per second. which corersponds to 400 packets per second.
        #If scheduled 400 packets, break the loop. Maximum of 1000 times the loop will be executed.
        scheduled_packet_count = 0 
        
        trial_count = 0
        while scheduled_packet_count < self.num_of_input_ports *self.distribution_mean and trial_count < self.num_of_input_ports *self.distribution_mean*2:
            min_arrival_time = float('inf')
            selected_queue = None
            trial_count += 1
            for i, input_queue in enumerate(self.input_queues):
                
                if not input_queue.empty():
                    head_of_line_packet = input_queue.queue[0] # Peek at the head of the queue
                    
                    if head_of_line_packet.arrival_time < min_arrival_time:
                        min_arrival_time = head_of_line_packet.arrival_time
                        selected_queue = i
            # If a packet is found, dequeue and enqueue it to the output queue
            if selected_queue is not None:
                selected_packet = self.input_queues[selected_queue].get() # Dequeue the packet
                self.output_queue.put(selected_packet) # Enqueue the packet to the output queue
                scheduled_packet_count += 1
            

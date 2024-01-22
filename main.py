from fifo_scheduler import FIFOScheduler
from pifo_scheduler import PIFOScheduler
NUM_PORTS = 4

scheduler = FIFOScheduler(NUM_PORTS)
#scheduler = PIFOScheduler(NUM_PORTS)
scheduler.start_simulation()
scheduler.plot_data()


import time


class Clock:
    def __init__(self, frequency_hz: float):
        self.frequency_hz = frequency_hz
        self.cycle_duration = 1.0 / frequency_hz
        self.last_tick = time.perf_counter()
        self.ticks = 0

    def wait_cycles(self, cycles: int):
        self.ticks += cycles
        target_time = self.last_tick + (self.cycle_duration * cycles)
        while time.perf_counter() < target_time:
            pass  # Busy wait
        self.last_tick = time.perf_counter()

    def adjust_for_elapsed_time(self):
        # Adjust the last_tick for time spent outside the clock, ensuring timing remains accurate
        now = time.perf_counter()
        if now - self.last_tick > self.cycle_duration:
            self.last_tick = now - self.cycle_duration

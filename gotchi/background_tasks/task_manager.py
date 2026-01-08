# gotchi/background_tasks/task_manager.py
"""Module to manage background tasks for the game.
"""

import threading
import atexit

class TaskManager:
    """Class to manage background tasks for the application."""

    threads = []

    def __init__(self):
        #TODO: Replace None with actual hunger management function
        hunger_thread = threading.Thread(target=None)
        self.threads.append(hunger_thread)

        atexit.register(self.stop_background_tasks)

    def start_background_tasks(self):
        """Function to start background tasks for the application."""
        for thread in self.threads:
            thread.start()

    def stop_background_tasks(self):
        """Function to stop all background tasks gracefully."""
        for thread in self.threads:
            thread.join()

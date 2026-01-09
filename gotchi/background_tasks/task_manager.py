# gotchi/background_tasks/task_manager.py
"""Module to manage background tasks for the game.
"""

import time

from gotchi.background_tasks import hunger


def task_loop(app):
    """Function to run the task loop (every minute) for background tasks."""
    tasks = []
    tasks.append(hunger.task)

    while True:
        print(
            f"{time.strftime('%H:%M:%S')} : Task manager loop executing tasks...", flush=True)
        for task in tasks:
            print(
                f"{time.strftime('%H:%M:%S')} : Executing task: {task.__module__}", flush=True)
            status = task(app)
            print(
                f"{time.strftime('%H:%M:%S')} : Task executed with status: {status}", flush=True)

        time.sleep(60)

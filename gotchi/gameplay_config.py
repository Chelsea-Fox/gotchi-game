# gotchi/gameplay_config.py
"""gameplay configuration settings for Gotchi.
"""

GAMEPLAY_CONFIG = {
    # HUNGER
    "starving_threshold": 0,  # Threshold to consider a Gotchi starving
    "hungry_threshold": 25,  # Threshold to consider a Gotchi hungry
    "full_threshold": 100,  # Threshold to consider a Gotchi full
    "hunger_decrease_interval_seconds": 60,  # Interval to decrease hunger levels
    "hunger_decrease_amount": 10,  # Amount to decrease hunger by each period
    "health_decrease_when_starving": 5,  # Amount to decrease health when starving
    "hunger_increase_on_feed": 20  # Amount to increase hunger by when fed
}

"""
Memory management module.
"""


class Memory:
    """
    Manages observations and action outcomes.
    """

    def __init__(self):
        self.observations = []
        self.action_outcomes = []

    def update_memory(self, observation, outcome):
        """
        Updates memory with a new observation and its outcome.
        """
        self.observations.append(observation)
        self.action_outcomes.append(outcome)

    def get_latest(self):
        """
        Retrieves the latest observation and outcome.
        """
        return self.observations[-1], self.action_outcomes[-1]

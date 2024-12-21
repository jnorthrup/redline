class Memory:
    def __init__(self):
        self.observations = []
        self.action_outcomes = []

    def update_memory(self, observation, outcome):
        self.observations.append(observation)
        self.action_outcomes.append(outcome)

    def get_latest(self):
        return self.observations[-1], self.action_outcomes[-1]

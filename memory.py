class Memory:
    def __init__(self):
        self.observations = []
        self.action_outcomes = []
        self.bias = 1.0

    def update_memory(self, observation, outcome):
        print(f"Updating memory with observation: {observation}, outcome: {outcome}")
        self.observations.append(observation)
        self.action_outcomes.append(outcome)

    def get_latest(self):
        try:
            latest_observation = self.observations[-1]
            latest_outcome = self.action_outcomes[-1]
        except IndexError:
            latest_observation = None
            latest_outcome = None
        print(f"Latest observation: {latest_observation}, Latest outcome: {latest_outcome}")
        return latest_observation, latest_outcome

    def revise_bias(self, revision):
        self.bias += revision

    def is_complete(self):
        # Determine if completion criteria are met
        return len(self.observations) > 0 and self.observations[-1] == "FINISH"

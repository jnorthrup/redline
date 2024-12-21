class RewardSystem:
    def __init__(self):
        pass

    def calculate_reward(self, technical_debt, tokens_needed):
        return technical_debt / (tokens_needed**3)

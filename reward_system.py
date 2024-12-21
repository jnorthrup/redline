class RewardSystem:
    def __init__(self):
        pass

    def calculate_reward(self, technical_debt, tokens_needed):
        reward = technical_debt / (tokens_needed ** 3)
        print(f"Calculating reward: {reward} for technical debt: {technical_debt}, tokens needed: {tokens_needed}")
        return reward

    def apply_reward(self, agent, technical_debt, tokens_needed):
        reward = self.calculate_reward(technical_debt, tokens_needed)
        agent.update_bias(reward)

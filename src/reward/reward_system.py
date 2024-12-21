class RewardSystem:
    def __init__(self):
        self.technical_debt = 0
        self.tokens_needed = 1  # Avoid division by zero

    def update_technical_debt(self, debt):
        self.technical_debt += debt

    def set_tokens_needed(self, tokens):
        self.tokens_needed = tokens if tokens > 0 else 1  # Ensure tokens_needed is positive

    def calculate_reward(self):
        if self.tokens_needed <= 0:
            return 0
        return self.technical_debt / (self.tokens_needed ** 3)
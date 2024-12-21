class SupervisorConfig:
    # ...existing code...

    def calculate_reward(
        self, technical_debt_offset: float, tokens_needed: int
    ) -> float:
        """
        Calculate the reward based on technical debt offset and tokens needed.
        """
        return technical_debt_offset / (tokens_needed**3)

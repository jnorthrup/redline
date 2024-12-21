class Memory:
    def __init__(self):
        self.memory_store = []

    def update_memory(self, observation):
        self.memory_store.append(observation)

    def get_latest(self, count=1):
        return self.memory_store[-count:] if count <= len(self.memory_store) else self.memory_store
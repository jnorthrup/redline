"""
Memory Manager module.
"""


class MemoryManager:
    """
    Class to manage memory.
    """

    def __init__(self):
        self.memory_store = []

    def update_memory(self, observation):
        """
        Adds a memory.
        """
        self.memory_store.append(observation)

    def get_latest(self, count=1):
        """
        Retrieves the latest memories.
        """
        return (
            self.memory_store[-count:]
            if count <= len(self.memory_store)
            else self.memory_store
        )

class CompletionAgent(Agent):
    def __init__(self, name, memory, tools):
        super().__init__(name, memory, tools)

    def verify_completion(self, task_requirements):
        # Logic to verify if the task has been completed satisfactorily
        if self.memory.get_latest() == task_requirements:
            return True
        return False

    def issue_completion_status(self):
        if self.verify_completion(self.memory.get_latest()):
            return "FINISH"
        return "INCOMPLETE"
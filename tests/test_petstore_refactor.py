def fetch(self, item):
    return f"{self.name} fetched {item}!"


class Cat(Pet):
    def __init__(self, name):
        super().__init__(name, "cat")

    def scratch(self, item):
        return f"{self.name} scratched {item}!"


def global_function(x):
    return x * 2

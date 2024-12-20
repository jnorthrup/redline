import threading


class ProviderListingThread(threading.Thread):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProviderListingThread, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            super(ProviderListingThread, self).__init__()
            self.daemon = True
            self.initialized = True

    def run(self):
        # Implement provider listing logic here
        pass

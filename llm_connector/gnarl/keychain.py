"""Keychain module."""

import os
from keyring import set_password, get_password

class Keychain:
    """Keychain class docstring."""

    def __init__(self, service_name):
        self.service_name = service_name

    def set_api_key(self, api_key):
        """Set API key in keychain."""
        set_password(self.service_name, 'api_key', api_key)

    def get_api_key(self):
        """Get API key from keychain."""
        return get_password(self.service_name, 'api_key')

    def add_to_keys(self, key_name):
        """Add API key to KEYS keychain."""
        api_key = os.environ.get(f'{key_name}_API_KEY')
        if api_key:
            set_password('KEYS', key_name, api_key)

# Example usage
if __name__ == "__main__":
    keychain = Keychain('OpenRouter')
    keychain.set_api_key(os.environ.get('OPENROUTER_API_KEY'))
    print("API key stored in keychain.")
    keychain.add_to_keys('OpenRouter')
    print("API key added to KEYS keychain.")
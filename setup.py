from setuptools import setup, find_packages

setup(
    name="redline",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'ollama',
        'litellm',
        'GitPython',  # For git operations in ExecutionAgent
        'typing-extensions',  # For better type hints
    ],
    python_requires='>=3.8',
)

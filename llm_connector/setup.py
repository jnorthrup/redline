from setuptools import setup, find_packages

setup(
    name='llm_connector',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'llm-connector=llm_connector.gnarl.supervisor:main',
        ],
    },
)
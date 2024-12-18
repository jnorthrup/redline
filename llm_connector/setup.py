from setuptools import setup, find_packages

setup(
    name='llm_connector',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'asyncio',
        'typing',
        'statistics'
    ],
    entry_points={
        'console_scripts': [
            'llm-connector=llm_connector.main:main',
            'llm-connector-supervisor=llm_connector.gnarl.supervisor:main'
        ],
    },
    package_dir={'': '.'},
    python_requires='>=3.7',
)

from setuptools import setup, find_packages

setup(
    name='openclaw-config-manager',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'gitpython==3.1.40',
        'jsonschema==4.20.0',
    ],
    entry_points={
        'console_scripts': [
            'openclaw-config-manager=openclaw_config_manager.cli:main',
        ],
    },
    author='OpenClaw Team',
    description='Git-based configuration manager for OpenClaw',
    license='MIT',
)
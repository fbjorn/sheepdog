from setuptools import find_packages, setup

setup(
    name='sheepdog',
    version='0.0.1',
    description='Website monitoring service',
    author='fbjorn',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'aiohttp',
        'aiohttp-jinja2',
        'loguru',
        'schema',
    ],
    entry_points={
        'console_scripts': [
            'run_server=sheepdog.server:start_server'
        ],
    },
)

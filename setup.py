from setuptools import find_packages
from setuptools import setup

setup(
        name='rpi_hardware',
        version='0.2.1',
        packages=find_packages(),
        url='https://github.com/sacherjj/rpi_hardware/',
        license='MIT License',
        author='Joe Sacher',
        author_email='sacherjj@gmail.com',
        description='Package with Raspberry Pi Hardware Drivers and Mocking GPIO and smbus.'
)

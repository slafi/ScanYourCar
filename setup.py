from setuptools import setup

with open("Readme.md", 'r') as f:
    long_description = f.read()

setup(
   name='ScanYourCar',
   version='1.0',
   description='The ScanYourCar project connects to the car through an OBD reader (e.g., ELM327) and checks which PIDs (Mode 2 and Mode 3 only) are supported by that car. It also gets a snapshot of the data for each supported PID.',
   author='Sabeur Lafi',
   author_email='lafi.saber@gmail.com',
   url="https://github.com/slafi",
   license="MIT",
   long_description=long_description,
   packages=['explorer'],
)
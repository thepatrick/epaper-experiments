import sys, os
from setuptools import setup

dependencies = ['Pillow', 'numpy', 'roonapi']

if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    dependencies += ['RPi.GPIO', 'spidev']
else:
    dependencies += ['Jetson.GPIO']

setup(
    name='thepatrick-epaper-expermints',
    description='@thepatrick e-Paper experiments',
    author='thepatrick',
    package_dir={'': 'lib'},
    # packages=['waveshare_epd'],
    install_requires=dependencies,
)


# Change to the directory containing this file and use the command
# python3 setup.py sdist
# to build a source distribution

from distutils.core import setup

# Use the readme file as the long description
from os import path
sunrise_sunset_directory = path.abspath(path.dirname(__file__))
readme_file = open(path.join(sunrise_sunset_directory, 'README.md')) 
readme = readme_file.read()

setup(name='sunrise_sunset',
      version = '1.2.1',
      py_modules = ['sunrise_sunset'],
      description='Calculates sunrise and sunset times based on date and location',
      long_description=readme,
      author='Paul Ivinson',
      # author_email='unknown@example.com' - creates a warning but we'll ignore it.
      url='https://github.com/Paul-Ivinson/sunrise_sunset',
      #copyright='Copyright 2022 Paul Ivinson',
      license='GPLv3',
      #packages=['sunrise_sunset'],
      scripts = ["sunrise_sunset.py"],
      requires=["dateutil"]
      #dependencies = ["dateutil"]
)

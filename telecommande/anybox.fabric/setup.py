from setuptools import setup, find_packages

VERSION = 0.1

setup(
    name='anybox.fabric',
    version=VERSION,
    description="Remote control for the Anybox hosting infrastructure",
    author="Anybox",
    author_email="contact@anybox.fr",
    license="GPLv3+",
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read())),
    namespace_packages=['anybox'],
    packages=find_packages(),
    install_requires=['setuptools', 'Fabric', 'jinja2', 'reg'],
    entry_points="")

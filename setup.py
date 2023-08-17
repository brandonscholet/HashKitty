from setuptools import setup, find_packages

setup(
    name='HashcatHerder',
    version='0.1.0',
    description='herds your (hash)cats',
    author='Brandon',
    author_email='brandon@scholet.net',
    url='https://github.com/brandonscholet/HashcatHerder',
    packages=find_packages(),
    install_requires=[
        'bs4',
    ],
	entry_points={
        'console_scripts': [
            'HashcatHerder = HashcatHerder.main:do_the_thing',
        ],
    },
)

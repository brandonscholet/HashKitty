from setuptools import setup, find_packages

setup(
    name='HashKitty',
    version='0.220',
    description='herds your (hash)cats',
    author='Brandon',
    author_email='brandon@scholet.net',
    url='https://github.com/brandonscholet/HashKitty',
    packages=find_packages(),
    install_requires=[
        'bs4',
    ],
	entry_points={
        'console_scripts': [
            'HashKitty = HashKitty.main:do_the_thing',
        ],
    },
)

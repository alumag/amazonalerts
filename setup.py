from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AmazonAlerts',
    version='1.0.0',
    packages=['AmazonAlerts'],
    install_requires=required,
    url='https://github.com/MissLummie/amazon-alerts',
    license='',
    author='Aluma Gelbard',
    author_email='violetaluma@hotmail.com',
    description='Send announcements in discord on your great new amazon deals',
    long_description=long_description,
    long_description_content_type='text/markdown'
)

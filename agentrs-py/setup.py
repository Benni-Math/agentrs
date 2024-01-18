from setuptools import setup, find_packages


long_description = open('README.md').read()

# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

version = '0.1.0'

setup(
    name='agentrs',
    version=version,
    install_requires=[
        'agentrs_core'
    ],
    author='Benedikt Arnarsson',
    author_email='benediktjens.arnarsson@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/Benni-Math/agentrs/',
    license='MIT',
    description='Build fast ABMs in Python, with the help of Rust.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

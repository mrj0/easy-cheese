from setuptools import setup, find_packages


setup(
    name="easy-cheese",
    version="0.1",
    description="Easily prepare a Python package for the cheese shop",
    url="https://github.com/mrj0/easy-cheese",
    author="Mike Johnson",
    author_email="mike@publicstatic.net",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7"
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development",
    ],
    entry_points={
        'console_scripts': [
            'easy-cheese = easy_cheese.main:main',
        ]},
)

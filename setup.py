from setuptools import setup

setup(
    name='photo-sorter CLI',
    version='0.1.2',
    author='Christopher Hoogeboom',
    py_modules=['photo_sorter'],
    install_requires=[
        'Click', 'ExifRead'
    ],
    entry_points='''
        [console_scripts]
        sort-photos=photo_sorter:cli
    ''',
)
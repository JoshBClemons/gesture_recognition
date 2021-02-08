from setuptools import setup


def readme():
    """Import the README.md Markdown file and try to convert it to RST format."""
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except(IOError, ImportError):
        with open('README.md') as readme_file:
            return readme_file.read()

setup(
    name='motion_identification',
    version='0.1',
    description='Motion Identification',
    long_description=readme(),
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    url='https://github.com/JoshBClemons/motion_identification',
    author='Joshua Clemons', 
    author_email='clemonsjoshua6@gmail.com',  
    license='MIT',
    packages=['motion_identification'],
    install_requires=[
        'pypandoc>=1.4', # replace with current versions
        'keras==2.4.3',
        'numpy==1.20.1',
        'opencv-contrib-python==4.5.1.48',       
        'flask==1.1.2', 
        'Pillow==8.1.0',
        'pytest==6.2.2',
        'pytest-runner==5.2',
        'tensorflow==2.4.1',
        'h5py==2.10.0',
        ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)

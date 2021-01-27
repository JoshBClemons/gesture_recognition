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
        'Programming Language :: Python :: 3',
    ],
    url='https://github.com/JoshBClemons/motion_identification',
    author='Josh Clemons',  # Substitute your name
    author_email='clemonsjoshua6@gmail.com',  # Substitute your email
    license='NA',
    packages=['motion_identification'],
    install_requires=[
        'pypandoc>=1.4', # replace with current versions
        'watermark>=1.8.1',
        'pandas>=0.24.2',
        'scikit-learn>=0.20.3',
        'scipy>=1.2.1',
        'matplotlib>=3.0.3',
        'pytest>=4.3.1',
        'pytest-runner>=4.4',
        'click>=7.0',
        'opencv-contrib-python',       
        'imagezmq',
        'imutils',   
        'flask', 
        'joblib',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
        [console_scripts]
        motion_identification_analysis=motion_identification.command_line:motion_identification_analysis
    '''
)
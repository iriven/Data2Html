# installation: pip install nested-lookup
from setuptools import setup, find_packages

# get list of requirement strings from requirements.txt
def remove_whitespace(x):
    return ''.join(x.split())

def sanitize(x):
    return not x.startswith('#') and x != ''

def requirements():
    with open('requirements.pip', 'r') as f:
        r = f.readlines()
    map(remove_whitespace, r)
    filter(sanitize, r)
    return r

if __name__ == '__main__':
    print(requirements())
    setup(
        name='ifileconverter',
        package_dir={'': 'src'},
        packages=find_packages(where="src"),
        version='0.1.0',
        description='Converts Yaml file to HTML tabular representation',
        long_description=open('README.md', 'r', encoding='utf-8').read(),
        long_description_content_type='text/markdown',
        keywords = ['yaml', 'HTML', 'converter', 'json', 'csv', 'Table', 'xml'],
        author='Alfred TCHONDJO',
        author_email='atchondjo@gmail.com',
        url='https://github.com/iriven/iDataProcessor',
        download_url = 'https://github.com/iriven/iDataProcessor/archive/refs/heads/main.zip',
        project_urls={
            'Bug Tracker': 'https://github.com/iriven/iDataProcessor/issues',
        },
        classifiers=[
                # this library supports the following Python versions.
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
            ],
        license='MIT',
        platforms=['All'],
        include_package_data=True,
        py_modules=['ifileconverter'],
        install_requires=['pkgutil','pyyaml','xmltodict'],
        python_requires='>=3.6',
    )

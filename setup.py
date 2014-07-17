import os
from setuptools import setup, find_packages

version = "1.0"

description = """
    Planning with diffeomorphisms
"""

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
long_description = read('README.md')
    

setup(name='diffeoplan',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/diffeoplan',
      
      description=description,
      long_description=long_description,
      keywords="planning",
      license="LGPL",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        # 'Topic :: Software Development :: Quality Assurance',
        # 'Topic :: Software Development :: Documentation',
        # 'Topic :: Software Development :: Testing'
      ],

	  version=version,
      download_url='http://github.com/AndreaCensi/diffeoplan/tarball/%s' % version,
      
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=['networkx' ],
      tests_require=['nose'],
      entry_points={
        'console_scripts': [
                            'dp = diffeoplan:dpmain',
                            'dptr1 = dptr1:dptr1_main',
                            ]
    },
)


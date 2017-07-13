#!/usr/bin/env python

from setuptools import setup

long_description = """
=======
SEGYVIEWER
=======

Segyviewer is a small LGPL licensed python library for easy viewing of SEG-Y
files. It uses the segyio library for reading files.


"""

requires = map(str.rstrip, open('requirements.txt').readlines())

setup(name='segyviewlib',
      use_scm_version={'write_to': 'version.py'},
      description='Simple viewer library for SEG-Y files',
      long_description=long_description,
      author='Statoil ASA',
      author_email='fg_gpl@statoil.com',
      url='https://github.com/Statoil/segyviewer',
      install_requires=requires,
      setup_requires=['setuptools_scm'],
      packages=['segyviewlib'],
      test_suite='tests',
      package_dir={'': 'src'},
      package_data={'':
                        ['LICENSE',
                         'README.md',
                         'resources/img/350px-SEGYIO.png',
                         'resources/img/cog.png',
                         'resources/img/layouts_four_grid.png',
                         'resources/img/layouts_three_bottom_grid.png',
                         'resources/img/layouts_three_left_grid.png',
                         'resources/img/layouts_three_top_grid.png',
                         'resources/img/layouts_two_horizontal_grid.png',
                         'resources/img/folder.png',
                         'resources/img/layouts_single.png',
                         'resources/img/layouts_three_horizontal_grid.png',
                         'resources/img/layouts_three_right_grid.png',
                         'resources/img/layouts_three_vertical_grid.png',
                         'resources/img/layouts_two_vertical_grid.png',
                         'resources/img/table_export.png',
                         'resources/img/readme.txt'
                         ]},
      license='LGPL-3.0',
      platforms='any',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities'
      ]
      )
setup(name='segyviewer',
      use_scm_version=True,
      description='Simple viewer for SEG-Y files',
      long_description=long_description,
      author='Statoil ASA',
      author_email='fg_gpl@statoil.com',
      url='https://github.com/Statoil/segyviewer',
      install_requires=['segyviewlib'],
      setup_requires=['setuptools_scm'],
      scripts=['applications/segyviewer'],
      license='LGPL-3.0',
      platforms='any',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities'
      ]
      )

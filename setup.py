from setuptools import setup

version = '1.0.2dev'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open('TODO.txt').read(),
    open('CREDITS.txt').read(),
    open('CHANGES.txt').read(),
    ])

install_requires = [
    'Django',
    'django-staticfiles',
    'django-extensions',
    'django-piston',
    'lizard-map > 1.42',
    'lizard-ui',
    'django-nose',
    'iso8601',
    ],

tests_require = [
    ]

setup(name='lizard-fewsjdbc',
      version=version,
      description=("Lizard-map plugin for showing FEWS " +
                   "data through a jdbc connection"),
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='TODO',
      author_email='TODO@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_fewsjdbc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
            ],
          'lizard_map.adapter_class': [
            'adapter_fewsjdbc = lizard_fewsjdbc.layers:FewsJdbc'
            ],
          },
      )

from setuptools import setup

version = '2.28.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'ciso8601',
    'django-braces',
    'django-extensions',
    'django-nose',
    'django-staticfiles',
    'django-tls',
    'djangorestframework',
    'factory_boy',
    'iso8601',
    'lizard-map >= 4.0, < 5.0',
    'lizard-ui >= 4.0, < 5.0',
    'pkginfo',
    'pytz',
    'south',
    'translations',
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
      author='Jack Ha',
      author_email='jack.ha@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_fewsjdbc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
            ],
          'lizard_map.adapter_class': [
            'adapter_fewsjdbc = lizard_fewsjdbc.layers:FewsJdbc'
            ],
          'lizard_datasource': [
            'lizard_fewsjdbc = lizard_fewsjdbc.datasource:factory'
            ],
          },
      )

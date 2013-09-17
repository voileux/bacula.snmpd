from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='bacula.snmpd',
      version=version,
      description="Demon SNMP pour Bacula",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bacula'],
      include_package_data=True,
      data_files = [('etc', ['src/templates/etc/defaults.cfg'])],
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'SQLAlchemy',
          'zope.sqlalchemy',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      snmpd-server = bacula.snmpd.server:main
      """,
      )

      #snmpd-server = bacula.snmpd.server:main

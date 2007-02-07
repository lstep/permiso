# -*- coding: utf-8 -*-
"""
Copyright (C) 2007 Adelux <contact@adelux.fr>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
from setuptools import setup, find_packages
import sys, os

from permiso import collector

setup(name='permiso.collector',
      version=collector.__version__,
      namespace_packages = ['permiso'],
      description="Collector for IP Queue module",
      long_description="""\
This programs is part of the Permiso Framework. It collects the packets sent from the firewall module ip_queue""",
      keywords='adelux permiso linux python firewall security listener queue ip iptables nf_queue',
      author='Luc Stepniewski',
      author_email='luc.stepniewski@adelux.fr',
      url='http://code.google.com/p/collector',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = {
          'collectordata': ['data/bin/*',],
      },
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
	  #"Twisted==2.4.0",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      collector-admin = collector.command:main
      """,
      # Voir http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Communications'],

      test_suite = "permiso.collector.tests",
      )
      

#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Drugs-Harvesters -- Harvesters to collect data on medications
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Etalab
# http://github.com/eraviart/drugs-harvesters
#
# This file is part of Drugs-Harvesters.
#
# Drugs-Harvesters is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Drugs-Harvesters is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Harvesters to collect data on medications"""


from setuptools import setup


setup(
    name = 'drugs-harvesters',
    version = '0.1',

    author = 'Emmanuel Raviart',
    author_email = 'emmanuel@raviart.com',
    description = 'Harvesters to collect data on medications',
    url = 'http://github.com/eraviart/drugs-harvesters',

    install_requires = [
        'lxml',
        'requests',
        ],
    packages = [],
    )

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


"""Download drugs pages from http://base-donnees-publique.medicaments.gouv.fr"""


import argparse
import codecs
import itertools
import json
import logging
import os
import shutil
import sys
import urlparse

import lxml.html
import requests


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
site_url = 'http://base-donnees-publique.medicaments.gouv.fr/'


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-a', '--all', action = 'store_true', help = 'download all pages')
    parser.add_argument('-d', '--download-dir', default = 'base-donnees-publique.medicaments.gouv.fr',
        help = 'directory where to store downloaded pages')
    parser.add_argument('-i', '--index', action = 'store_true', help = 'download index pages')
    parser.add_argument('-p', '--pages', action = 'store_true', help = 'download drugs pages')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'increase output verbosity')

    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)

    if not os.path.exists(args.download_dir):
        os.makedirs(args.download_dir)

    index_path = os.path.join(args.download_dir, 'index.json')
    if args.all or args.index:
        drug_name_by_url_path = {}
        form_data = dict(
            affliste = 1,
            affNumero = 0,
            choixRecherche = 'medicament',
            inClauseSubst = 0,
            isAlphabet = 0,
#            nomSubstances =
            page = 1,
            radLibelle = 2,
            radLibelleSub = 4,
#            txtCaracteresSub =
#            txtCaracteres =
            typeRecherche = 0,
            )
        for page_number in itertools.count(1):
            log.info(u'Harvesting index page {}'.format(page_number))
            form_data['page'] = page_number
            response = requests.post(urlparse.urljoin(site_url, 'index.php'), data = form_data)
            html_element = lxml.html.fromstring(response.content)
            a_element_list = html_element.xpath('//table[@class="result"]//a[@class="standart"]')
            if not a_element_list:
                break
            for a_element in a_element_list:
                drug_name_by_url_path[a_element.get('href')] = a_element.text.strip()
        with codecs.open(index_path, 'w', encoding = 'utf-8') as index_file:
            json.dump(drug_name_by_url_path, index_file, ensure_ascii = False, indent = 2, sort_keys = True)
    else:
        with codecs.open(index_path, encoding = 'utf-8') as index_file:
            drug_name_by_url_path = json.load(index_file)

    if args.all or args.pages:
        pages_dir = os.path.join(args.download_dir, 'pages')
        if os.path.exists(pages_dir):
            shutil.rmtree(pages_dir)
        os.makedirs(pages_dir)

        for url_path, drug_name in sorted(drug_name_by_url_path.iteritems()):
            drug_id = url_path.rsplit('=', 1)[-1]
            log.info(u'Harvesting drug {}: {}'.format(drug_id, drug_name))
            response = requests.get(urlparse.urljoin(site_url, url_path))
            drug_path = os.path.join(pages_dir, 'page-{}.html'.format(drug_id))
            with open(drug_path, 'w') as drug_file:
                for chunk in response.iter_content(8192):
                    drug_file.write(chunk)

    return 0


if __name__ == "__main__":
    sys.exit(main())

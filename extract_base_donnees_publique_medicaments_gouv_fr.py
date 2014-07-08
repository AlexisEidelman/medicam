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


"""Extract data from pages downloaded from http://base-donnees-publique.medicaments.gouv.fr"""


import argparse
import codecs
import collections
import datetime
import json
import logging
import os
import re
import sys

import lxml.html


app_name = os.path.splitext(os.path.basename(__file__))[0]
authorization_holder_re = re.compile(ur"Titulaire de l'autorisation : (?P<name>.+)$")
cip_codes_re = re.compile(ur'Code CIP : (?P<cip_code0>[- \d]+) ou (?P<cip_code1>[- \d]+)$')
cis_code_re = re.compile(ur'Code CIS :  (?P<cis_code>.+)$')
conditioning_re = re.compile(ur'(?P<type>.+) \(Composition (pour (?P<quantity>.+))?\)$')
drug_filename_re = re.compile(ur'page-(?P<drug_id>\d+)\.html$')
log = logging.getLogger(app_name)
price_line_re = re.compile(ur'Prix : (?P<price>\d+(,\d{1,2})?) € +Taux de remboursement : (?P<refund_rate>\d+) %$')
marketing_date_re = re.compile(
    ur"Déclaration(?P<stop> d'arrêt)? de commercialisation : (?P<day>\d{2})/(?P<month>\d{2})/(?P<year>\d{4})$")


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-d', '--download-dir', default = 'base-donnees-publique.medicaments.gouv.fr',
        help = 'directory where to store downloaded pages')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'increase output verbosity')

    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)

    assert os.path.exists(args.download_dir), 'Missing directory: {}'.format(args.download_dir)
    pages_dir = os.path.join(args.download_dir, 'pages')
    assert os.path.exists(pages_dir), 'Missing directory: {}'.format(pages_dir)

    drugs = []
    for drug_filename in sorted(os.listdir(pages_dir)):
        match = drug_filename_re.match(drug_filename)
        if match is None:
            log.info(u'Skipping file: {}'.format(drug_filename))
            continue
        drug_id = int(match.group('drug_id'))
        page_doc = lxml.html.parse(os.path.join(pages_dir, drug_filename))

        h1_elements = page_doc.xpath('//h1[@class="textedeno"]')
        if not h1_elements:
            log.info(u'Skipping empty page {}'.format(drug_id))
            continue
        log.info(u'Parsing drug {}'.format(drug_id))

        drug_title = h1_elements[0].text.strip()

        generic_groups = [
            generic_group_element.text.strip()
            for generic_group_element in page_doc.xpath('//a[@name="Generiques"]/following-sibling::ul[1]/li/a')
            ]

        composition = []
        for composition_element in page_doc.xpath('//ul[@class="compo"]/li'):
            conditioning = composition_element.find('img').tail.strip()
            conditioning_match = conditioning_re.match(conditioning)
            assert conditioning_match is not None, conditioning.encode('utf-8')
            components = collections.OrderedDict()
            for component_element in composition_element.xpath('.//ul[@class="compo2"]/li'):
                component = component_element.text.strip().lstrip(u'>').lstrip()
                dosage = component_element.findtext('span').strip()
                components[component] = dosage
            composition.append(dict(
                components = components,
                quantity = conditioning_match.group('quantity'),
                type = conditioning_match.group('type'),
                ))

        presentations = []
        for title_element, marketing_date_element, price_element in zip(
                page_doc.xpath('//h2[@class="titrePresentation"]'),
                page_doc.xpath('//h2[@class="titrePresentation"]/following-sibling::br[1]'),
                page_doc.xpath('//div[@class="infosCnam"]'),
                ):
            title = title_element.text.strip().lstrip(u'>').lstrip()
            cip_codes_match = cip_codes_re.match(title_element.tail.strip())
            cip_codes = [cip_codes_match.group('cip_code0'), cip_codes_match.group('cip_code1')]

            marketing_date_match = marketing_date_re.match(marketing_date_element.tail.strip())
            if marketing_date_match.group('stop'):
                marketing_start_date = None
                marketing_stop_date = datetime.date(int(marketing_date_match.group('year')),
                    int(marketing_date_match.group('month')), int(marketing_date_match.group('day'))).isoformat()
            else:
                marketing_start_date = datetime.date(int(marketing_date_match.group('year')),
                    int(marketing_date_match.group('month')), int(marketing_date_match.group('day'))).isoformat()
                marketing_stop_date = None

            price_match = price_line_re.match(price_element.text.strip())
            price = int(price_match.group('price').replace(',', ''))  # price in cents
            refund_rate = int(price_match.group('refund_rate'))

            presentations.append(dict(
                cip_codes = cip_codes or None,
                marketing_start_date = marketing_start_date,
                marketing_stop_date = marketing_stop_date,
                price = price,
                refund_rate = refund_rate,
                title = title,
                ))

        iab = []
        for row_element in page_doc.xpath('//a[@name="SMR"]/following-sibling::table[1]//tr[@class="TableRow"]'):
            cell_elements = row_element.findall('td')
            iab.append(dict(
                abstract = cell_elements[3].text.strip() or None,
                advice = cell_elements[1].text.strip() or None,
                reason = cell_elements[2].text.strip() or None,
                value = cell_elements[0].text.strip() or None,
                ))

        iab_improvements = []
        for row_element in page_doc.xpath('//a[@name="ASMR"]/following-sibling::table[1]//tr[@class="TableRow"]'):
            cell_elements = row_element.findall('td')
            iab_improvements.append(dict(
                abstract = cell_elements[3].text.strip() or None,
                advice = cell_elements[1].text.strip() or None,
                reason = cell_elements[2].text.strip() or None,
                value = cell_elements[0].text.strip() or None,
                ))

        authorization_holder = None
        cis_code = None
        for info_element in page_doc.xpath('//div[@id="autreInfo"]/ul/li'):
            info = info_element.text.strip()
            match = authorization_holder_re.match(info)
            if match is not None:
                authorization_holder = match.group('name')
            else:
                match = cis_code_re.match(info)
                if match is not None:
                    cis_code = match.group('cis_code')

        drugs.append(dict(
            authorization_holder = authorization_holder,
            cis_code = cis_code,
            composition = composition or None,
            generic_groups = generic_groups or None,
            iab = iab or None,
            iab_improvements = iab_improvements or None,
            id = drug_id,
            presentations = presentations or None,
            title = drug_title,
            ))

    drugs_path = os.path.join(args.download_dir, 'medicaments.json')
    with codecs.open(drugs_path, 'w', encoding = 'utf-8') as drugs_file:
        json.dump(drugs, drugs_file, ensure_ascii = False, indent = 2, sort_keys = True)

    return 0


if __name__ == "__main__":
    sys.exit(main())

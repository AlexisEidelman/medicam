#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Drugs-Harvesters -- Harvesters to collect data on medications
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2014 Etalab
# https://github.com/AlexisEidelman/medicam
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


"""Download ATC/DDD substances pages from http://www.whocc.no/"""


import argparse
import logging
import os
import re
import shutil
import sys
import urllib
import urllib2
import urlparse

import lxml.html


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
substance_url_re = re.compile(r'\./\?code=(?P<code>.+?)(&|$)')


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-d', '--download-dir', default = 'atc-ddd',
        help = 'directory where to store downloaded pages')
    parser.add_argument('-e', '--erase', action = 'store_true', help = 'erase pages already downloaded')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'increase output verbosity')

    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)

    if not os.path.exists(args.download_dir):
        os.makedirs(args.download_dir)

    codes = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    form_data = dict(
        code = None,
        showdescription = 'yes',
        )
    substance_by_code = {}
    while codes:
        code = codes.pop()
        form_data['code'] = code
        page_path = os.path.join(args.download_dir, '{}.html'.format(code))
        if not args.erase and os.path.exists(page_path):
            log.info(u'Reusing page for code {} (remaining: {})'.format(code, len(codes)))
            with open(page_path) as page_file:
                page = page_file.read()
        else:
            log.info(u'Harvesting page for code {} (remaining: {})'.format(code, len(codes)))
            response = urllib2.urlopen('http://www.whocc.no/atc_ddd_index/?{}'.format(urllib.urlencode(form_data)))
            page = response.read()
        html_element = lxml.html.fromstring(page)
        a_element_list = html_element.xpath('//div[@id="content"]/b/a')
        if not a_element_list:
            log.info('No substance with code {}'.format(code))
            continue
        hierarchy = [
            (
                substance_url_re.match(a_element.get('href')).group('code'),
                lxml.html.tostring(a_element, encoding = unicode, method = 'text').strip()
                )
            for a_element in a_element_list
            ]
        current_code, name =  hierarchy[-1]
        assert current_code == code
#        print hierarchy
        hierarchy_names = ([
            item[1]
            for item in hierarchy
            ] + [''] * 4)[:4]

        a_element_list = html_element.xpath('//div[@id="content"]/p/b/a')
        children = [
            (
                substance_url_re.match(a_element.get('href')).group('code'),
                lxml.html.tostring(a_element, encoding = unicode, method = 'text').strip()
                )
            for a_element in a_element_list
            ]
#        print children
        for child_code, child_name in children:
            codes.add(child_code)
        with open(page_path, 'w') as page_file:
            page_file.write(page)

        tr_element_list = html_element.xpath('//div[@id="content"]/ul/table/tr')
        if tr_element_list:
            labels = [
                td_element.text.strip()
                for td_element in tr_element_list[0].xpath('td')
                ]
            assert labels == [u'ATC code', u'Name', u'DDD', u'U', u'Adm.R', u'Note'], labels
            for tr_element in tr_element_list[1:]:
                values = [
                    lxml.html.tostring(td_element, encoding = unicode, method = 'text').strip()
                    for td_element in tr_element.xpath('td')
                    ]
                values[1:1] = hierarchy_names
                substance_by_code[values[0]] = values
    print u';'.join([
        u'ATC code',
        u'Anatomical Main Group',
        u'Therapeutic Subgroup',
        u'Pharmacological Subgroup',
        u'Chemical Subgroup',
        u'Chemical Substance',
        u'DDD',
        u'U',
        u'Adm.R',
        u'Note',
        ]).encode('utf-8')
    for code, values in sorted(substance_by_code.iteritems()):
        print u';'.join(values).encode('utf-8')

    return 0


if __name__ == "__main__":
    sys.exit(main())

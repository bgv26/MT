#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from lxml import etree
from config import DomClick


class EmptyResult(Exception):
    count = 0


def run():
    for cat in DomClick.DIRECTORIES:
        with open(os.path.join(cat, DomClick.LOG_FILE), 'w+', encoding='utf-8') as l:
            start_time = dt.now()
            l.write('+{}+\n'.format('-' * 78))
            l.write('|{:^78}|\n'.format('Start at: {}'.format(start_time.isoformat())))
            l.write('+{}+\n'.format('-' * 78))

            try:
                parser = etree.XMLParser(remove_blank_text=True)
                doc = etree.parse(os.path.join(cat, DomClick.IN_FILE), parser)
                root = doc.getroot()
                ns = {'dc': root.nsmap[None]}
                objects = doc.xpath('dc:offer', namespaces=ns)
            except IOError:
                doc = None
                objects = []

            total = len(objects)

            for obj in objects:
                try:
                    offer_id = obj.attrib['internal-id']

                    # Change organization, name, phone - замена телефона и названия организации
                    agent = obj.xpath('dc:sales-agent', namespaces=ns)[0]
                    organization = agent.xpath('dc:organization', namespaces=ns)[0]
                    name = agent.xpath('dc:name', namespaces=ns)[0]
                    phone = agent.xpath('dc:phone', namespaces=ns)[0]

                    old_phone = phone.text

                    if old_phone not in DomClick.OFFICES:
                        l.write('Blocked: unknown phone number "{}" in advert id [{}].\n'.format(old_phone, offer_id))
                        EmptyResult.count += 1
                        raise EmptyResult()

                    phone.text = DomClick.OFFICES[old_phone]['phone']
                    organization.text = DomClick.OFFICES[old_phone]['office']
                    name.text = DomClick.OFFICES[old_phone]['office']

                    # Change price - замена цены
                    price = obj.xpath('dc:price/dc:value', namespaces=ns)[0]
                    price.text = "%.2f" % (int(price.text) * DomClick.PRICE_RATIO)

                except EmptyResult:
                    pass

            if doc and total:
                with open(os.path.join(cat, DomClick.OUT_FILE), 'w+', encoding='utf-8') as f:
                    f.write(etree.tostring(doc,
                                           pretty_print=True,
                                           xml_declaration=True,
                                           encoding='utf-8').decode('utf-8'))

            exec_time = 'Script execution time: {} sec'
            conclusion = 'Totally parsed: {} offers. Blocked: {}.'

            current_time = dt.now()
            l.write('+{}+\n'.format('-' * 78))
            l.write('|{:^78}|\n'.format('Finish at: {}'.format(current_time.isoformat())))
            l.write('|{:^78}|\n'.format(exec_time.format((current_time - start_time).total_seconds())))
            l.write('|{:^78}|\n'.format(conclusion.format(total, EmptyResult.count)))
            l.write('+{}+\n'.format('-' * 78))


if __name__ == '__main__':
    run()

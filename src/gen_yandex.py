#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from lxml import etree
from config import Yandex


class EmptyResult(Exception):
    count = 0


def run():
    for cat in Yandex.DIRECTORIES:
        with open(os.path.join(cat, Yandex.LOG_FILE), 'w+', encoding='utf-8') as l:
            start_time = dt.now()
            l.write('+{}+\n'.format('-' * 78))
            l.write('|{:^78}|\n'.format('Start at: {}'.format(start_time.isoformat())))
            l.write('+{}+\n'.format('-' * 78))

            try:
                parser = etree.XMLParser(remove_blank_text=True)
                doc = etree.parse(os.path.join(cat, Yandex.IN_FILE), parser)
                root = doc.getroot()
                ns = {'ya': root.nsmap[None]}
                objects = doc.xpath('ya:offer', namespaces=ns)
            except IOError:
                doc = None
                objects = []

            total = len(objects)

            for obj in objects:
                try:
                    offer_id = obj.attrib['internal-id']

                    # Add hide-exact-address - скрытие точного расположения
                    location = obj.xpath('ya:location', namespaces=ns)[0]
                    etree.SubElement(location, 'hide-exact-address').text = 'true'

                    # Change organization, name, phone - замена телефона и названия организации
                    agent = obj.xpath('ya:sales-agent', namespaces=ns)[0]
                    organization = agent.xpath('ya:organization', namespaces=ns)[0]
                    name = agent.xpath('ya:name', namespaces=ns)[0]
                    phone = agent.xpath('ya:phone', namespaces=ns)[0]

                    old_phone = phone.text

                    if old_phone not in Yandex.OFFICES:
                        l.write('Blocked: unknown phone number "{}" in advert id [{}].\n'.format(old_phone, offer_id))
                        EmptyResult.count += 1
                        raise EmptyResult()

                    phone.text = Yandex.OFFICES[old_phone]['phone']
                    organization.text = Yandex.OFFICES[old_phone]['office']
                    name.text = Yandex.OFFICES[old_phone]['office']

                except EmptyResult:
                    pass

            if doc and total:
                with open(os.path.join(cat, Yandex.OUT_FILE), 'w+', encoding='utf-8') as f:
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

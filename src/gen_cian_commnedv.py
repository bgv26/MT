#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from lxml import etree

# definitions
HOME_DIR_MT = r'/export/cian'
HOME_DIR_NIRLAN = r'/export/n_cian'

DIRECTORIES = (
    # r'C:\Devel\PyCharmProject\MT\src',
    r'D:\Devel\MT\src',
    # os.path.join(HOME_DIR_MT, 'tem'),
    # os.path.join(HOME_DIR_MT, 'soc'),
    # os.path.join(HOME_DIR_MT, 'bud'),
    # os.path.join(HOME_DIR_MT, 'sev'),
    # os.path.join(HOME_DIR_MT, 'zap'),
    # os.path.join(HOME_DIR_MT, 'vos'),
    # os.path.join(HOME_DIR_MT, 'str'),
    # os.path.join(HOME_DIR_MT, 'bat'),
    # os.path.join(HOME_DIR_NIRLAN, 'centr'),
    # os.path.join(HOME_DIR_NIRLAN, 'sever'),
    # os.path.join(HOME_DIR_NIRLAN, 'zapad'),
)

# IN_FILE = 'bncat_comnedv.xml'
IN_FILE = 'bncat_comnedv_for_bn.xml'

# OUT_FILE = 'cian_comnedv_new.xml'
OUT_FILE = 'addresses.txt'

LOG_FILE = '{}-commerce.log'.format(dt.today().strftime('%d %B %Y %H-%M-%S'))

ID_PREFIX = "1508"

OFFICES = {
    '8(863)2-270-500': {'office': 'ДОНМТ офис Центральный 1', 'phone': '9381361278'},
    '8(863)2-990-707': {'office': 'ДОНМТ офис Центральный 2', 'phone': '9604434798'},
    '8(863)2-270-909': {'office': 'ДОНМТ офис Центральный 3', 'phone': '9286216057'},
    '8(863)200-67-67': {'office': 'ДОНМТ офис Западный', 'phone': '9298174480'},
    '8(863)2-300-909': {'office': 'ДОНМТ офис Северный', 'phone': '9885669794'},
    '8(863)2-500-400': {'office': 'ДОНМТ офис Северный', 'phone': '9885669794'},
    '8(863)200-85-85': {'office': 'ДОНМТ офис Стройгородок', 'phone': '9034067095'},
    '8(863)300-24-00': {'office': 'ДОНМТ офис Восточный', 'phone': '9045033362'},
    '8(863)2-417-423': {'office': 'ДОНМТ офис Батайск', 'phone': '9281879795'}
}

CONTRACT_TYPE = {
    'аренда': '1',
    'продажа': '4'
}


class BlockedRecordException(Exception):
    pass


class EmptyRequiredFieldException(Exception):
    pass


class EmptyResult(Exception):
    pass


def gen_new_id(offer_id):
    return ID_PREFIX + offer_id[4:]


def get_node_value(parent, node, required=False):
    try:
        value = parent.xpath(node)
        return value.pop().text.strip()
    except IndexError:
        ad_id = get_node_value(parent, 'id', True)
        if required:
            raise EmptyRequiredFieldException(
                'Blocked: empty required field ({}) in advert id [{}]'.format(node, ad_id))
        raise EmptyResult('Fix this: field {} in advert id: [{}] is  empty.'.format(node, ad_id))


def get_office_suffix(offer_id):
    return bytes([int(offer_id[9:])]).decode('cp1251')


def get_lot_number(offer_id):
    # symbols from 4 length 5 + '-8' + char value from three last digits in text
    return offer_id[4:9] + '-8' + get_office_suffix(offer_id)


def get_commerce_type(parent):
    object_type = get_node_value(parent, 'type', True)
    if object_type == 'офисы':
        return 'O'
    if object_type == 'склад':
        return 'W'
        # object_desc = get_node_value(parent, 'description/print', True)


def from_bn(item, log):
    try:
        description = get_node_value(item, 'description/full')
        ad_id = get_node_value(item, 'id', True)

        info = dict()

        info['ad_id'] = gen_new_id(ad_id)

        contract_type = get_node_value(item, 'action', True)
        info['contract_type'] = CONTRACT_TYPE[contract_type]

        info['area_total'] = get_node_value(item, 'total/value', True)

        info['floor_total'] = get_node_value(item, 'floors', True)
        info['floor'] = get_node_value(item, 'floor', True)

        info['price'] = get_node_value(item, 'price/value', True)
        if contract_type == 'аренда':
            info['price_period'] = get_node_value(item, 'price/period', True)

        agent_phone = get_node_value(item, 'agent/phone', True)
        info['phone'] = OFFICES[agent_phone]['phone']

        info['address_locality'] = get_node_value(item, 'location/city', True)
        info['address_street'] = get_node_value(item, 'location/street', True)

        info['photo'] = [photo.text for photo in item.xpath('files/image')]

        office = OFFICES[agent_phone]['office']
        lot_number = get_lot_number(ad_id)
        info['note'] = "{}\nПри звонке в {} укажите лот: {}".format(description, office, lot_number)

        return info

    except (EmptyRequiredFieldException, BlockedRecordException, EmptyResult) as e:
        log.write(str(e) + '\n')
        raise EmptyResult()


def to_cian(root_node, data):
    offer = etree.SubElement(root_node, 'object')
    ad_id = etree.SubElement(offer, 'ExternalId')
    ad_id.text = data['ad_id']
    rooms_num = etree.SubElement(offer, 'rooms_num')
    rooms_num.text = data['rooms_num']
    area = etree.SubElement(offer, 'area', total=data['area_total'])
    if 'area_living' in data:
        area.set('living', data['area_living'])
    if 'area_kitchen' in data:
        area.set('kitchen', data['area_kitchen'])
    price = etree.SubElement(offer, 'price', currency='RUB')
    price.text = data['price']
    floor = etree.SubElement(offer, 'floor', total=data['floor_total'])
    floor.text = data['floor']
    phone = etree.SubElement(offer, 'phone')
    phone.text = data['phone']
    etree.SubElement(offer, 'address', area='39', locality=data['address_locality'], street=data['address_street'])
    if 'options_mortgage' in data:
        etree.SubElement(offer, 'options', ipoteka=data['options_mortgage'])
    note = etree.SubElement(offer, 'note')
    note.text = etree.CDATA(data['note'])
    for p in data['photo']:
        photo = etree.SubElement(offer, 'photo')
        photo.text = p


for cat in DIRECTORIES:
    doc = etree.parse(os.path.join(cat, IN_FILE))
    with open(os.path.join(cat, OUT_FILE), 'w+', encoding='utf-8') as f, \
            open(os.path.join(cat, LOG_FILE), 'w+', encoding='utf-8') as l:
        objects = doc.xpath('bn-object')
        # commerces = [o for o in objects
        #              if o.xpath('type[text() = "квартира" or text() = "комната"]'
        #                                 ' and action[text() = "продажа"]')]
        # if len(commerces):
        #     root = etree.Element('commerce')
        #     for sale in commerces:
        #         try:
        #             to_cian(root, from_bn(sale, l))
        #         except EmptyResult:
        #             pass
        #     f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
        # types = set((o.xpath('type').pop().text for o in objects))
        # for t in types:
        #     f.write(t + '\n')
        # f.write('офисы\n')
        # o_s = [o for o in objects if o.xpath('type[text()="офисы"]')]
        # for i in o_s:
        #     f.write("o: {}".format(i.xpath('description/print').pop().text) + '\n')
        # f.write('\nторговые помещения\n')
        # t_s = [o for o in objects if o.xpath('type[text()="торговые помещения"]')]
        # for i in t_s:
        #     f.write("t: {}".format(i.xpath('description/print').pop().text) + '\n')
        # f.write('\nземельные участки\n')
        # zu_s = [o for o in objects if o.xpath('type[text()="земельные участки"]')]
        # for i in zu_s:
        #     f.write("zu: {}".format(i.xpath('description/print').pop().text) + '\n')
        # f.write('\nпомещения для сферы услуг\n')
        # bu_s = [o for o in objects if o.xpath('type[text()="помещения для сферы услуг"]')]
        # for i in bu_s:
        #     f.write("bu: {}".format(i.xpath('description/print').pop().text) + '\n')
        # f.write('\nпроизводственно-складские помещения\n')
        # wp_s = [o for o in objects if o.xpath('type[text()="производственно-складские помещения"]')]
        # for i in wp_s:
        #     f.write("wp: {}".format(i.xpath('description/print').pop().text) + '\n')
        # f.write('\n')
        for o in objects:
            f.write(o.xpath('location/address').pop().text + '\n')

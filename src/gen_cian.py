#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from lxml import etree

# definitions
HOME_DIR_MT = r'/export/cian'
HOME_DIR_NIRLAN = r'/export/n_cian'

DIRECTORIES = (
    r'C:\Devel\PyCharmProject\MT\src',
    # r'D:\Devel\MT\src',
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

IN_FILE = 'bncat.xml'

OUT_FILE = 'cian_new.xml'

LOG_FILE = '{}.log'.format(dt.today().strftime('%d %B %Y %H-%M-%S'))

ID_PREFIX = "1508"

BLOCK_PHRASES = (
    'ена 1',
    'ена 2',
    'ена: 1',
    'ена: 2',
    'найти',
    'Продажа квартир',
    'омощь',
    'оможем',
    'омогу',
    'выбрать квартиру',
    'выбор квартир',
    'квартир мало',
    'родажа',
    'квартир ',
    'варианты',
    '1-комнатные',
    '2х-комнатные',
    '1-2-3 комнатные',
    '1-2 комнатные',
    'Есть варианты по этажам',
    'квартиры на других этажах',
    'выбор квартир',
    'торговые площади',
)

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

DEAL_TYPE = {
    'аренда': 'R',
    'продажа': 'S'
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


def is_block(text):
    for block in BLOCK_PHRASES:
        if block in text:
            return True
    return False


def get_office_suffix(offer_id):
    return bytes([int(offer_id[9:])]).decode('cp1251')


def get_lot_number(offer_id):
    # symbols from 4 length 5 + '-8' + char value from three last digits in text
    return offer_id[4:9] + '-8' + get_office_suffix(offer_id)


def is_mortgage(item):
    try:
        ad_terms = get_node_value(item, 'additional-terms')
        return ad_terms == 'Ипотека'
    except EmptyResult:
        pass


def from_bn(item):
    description = get_node_value(item, 'description/full')
    ad_id = get_node_value(item, 'id', True)

    if is_block(description):
        raise BlockedRecordException('Blocked: bad description "{}" in advert id [{}]'.format(description, ad_id))

    info = dict()

    info['ad_id'] = gen_new_id(ad_id)

    info['price'] = str(int(get_node_value(item, 'price/value', True)) * 0.95)

    agent_phone = get_node_value(item, 'agent/phone', True)
    info['phone'] = OFFICES[agent_phone]['phone']

    info['address_locality'] = get_node_value(item, 'location/city', True)
    info['address_street'] = get_node_value(item, 'location/street', True)

    info['photo'] = [photo.text for photo in item.xpath('files/image')]

    office = OFFICES[agent_phone]['office']
    lot_number = get_lot_number(ad_id)
    info['note'] = "{}\nПри звонке в {} укажите лот: {}".format(description, office, lot_number)

    return info, ad_id


def from_bn_flats_and_rooms(item, log, sell=True):
    try:
        info, ad_id = from_bn(item)

        object_type = get_node_value(item, 'type', True)
        if object_type == 'квартира':
            if sell:
                info['options_mortgage'] = '1' if is_mortgage(item) else '0'
            info['rooms_num'] = get_node_value(item, 'rooms-total', True)
        else:
            info['rooms_num'] = '0'

        info['floor_total'] = get_node_value(item, 'floors', True)
        info['floor'] = get_node_value(item, 'floor', True)

        info['area_living'] = get_node_value(item, 'living/value')
        info['area_kitchen'] = get_node_value(item, 'kitchen/value')
        info['area_total'] = get_node_value(item, 'total/value', True)

        return info

    except (EmptyRequiredFieldException, BlockedRecordException, EmptyResult) as e:
        log.write(str(e) + '\n')
        raise EmptyResult()


def from_bn_suburbans(item, log):
    try:
        info, _ = from_bn(item)

        deal_type = get_node_value(item, 'action', True)
        info['deal_type'] = DEAL_TYPE[deal_type]
        info['realty_type'] = 'K'

        info['area_region'] = get_node_value(item, 'lot/value', True)
        info['area_living'] = get_node_value(item, 'total/value', True)
        info['floor_total'] = get_node_value(item, 'floors')
        info['options_year'] = get_node_value(item, 'building/year')

        return info

    except (EmptyRequiredFieldException, BlockedRecordException, EmptyResult) as e:
        log.write(str(e) + '\n')
        raise EmptyResult()


def to_cian_flats_and_rooms(root_node, data):
    offer = etree.SubElement(root_node, 'offer')
    ad_id = etree.SubElement(offer, 'id')
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


def to_cian_suburbans(root_node, data):
    offer = etree.SubElement(root_node, 'offer')
    ad_id = etree.SubElement(offer, 'id')
    ad_id.text = data['ad_id']
    deal_type = etree.SubElement(offer, 'deal_type')
    deal_type.text = data['deal_type']
    realty_type = etree.SubElement(offer, 'realty_type')
    realty_type.text = data['realty_type']
    etree.SubElement(offer, 'area', region=data['area_region'], living=data['area_living'])
    land_type = etree.SubElement(offer, 'land_type')
    land_type.text = '2'
    price = etree.SubElement(offer, 'price', currency='RUB')
    price.text = data['price']
    phone = etree.SubElement(offer, 'phone')
    phone.text = data['phone']
    etree.SubElement(offer, 'address', area='39', locality=data['address_locality'], street=data['address_street'])
    if 'options_year' in data and data['options_year']:
        etree.SubElement(offer, 'options', year=data['options_year'])
    for p in data['photo']:
        photo = etree.SubElement(offer, 'photo')
        photo.text = p
    if 'floor_total' in data and data['floor_total']:
        floor_total = etree.SubElement(offer, 'floor_total')
        floor_total.text = data['floor_total']
    note = etree.SubElement(offer, 'note')
    note.text = etree.CDATA(data['note'])


for cat in DIRECTORIES:
    doc = etree.parse(os.path.join(cat, IN_FILE))
    with open(os.path.join(cat, OUT_FILE), 'w+', encoding='utf-8') as f, open(os.path.join(cat, LOG_FILE), 'w+',
                                                                              encoding='utf-8') as l:
        objects = doc.xpath('bn-object')
        flats_rooms_sales = [o for o in objects
                             if o.xpath('type[text() = "квартира" or text() = "комната"]'
                                        ' and action[text() = "продажа"]')]
        if len(flats_rooms_sales):
            root = etree.Element('flats_for_sale')
            for sale in flats_rooms_sales:
                try:
                    to_cian_flats_and_rooms(root, from_bn_flats_and_rooms(sale, l))
                except EmptyResult:
                    pass
            f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
        flats_rooms_rents = [o for o in objects
                             if o.xpath('type[text() = "квартира" or text() = "комната"]'
                                        ' and action[text()="аренда"]')]
        if len(flats_rooms_rents):
            root = etree.Element('flats_rent')
            for sale in flats_rooms_rents:
                try:
                    to_cian_flats_and_rooms(root, from_bn_flats_and_rooms(sale, l, False))
                except EmptyResult:
                    pass
            if len(flats_rooms_sales):
                f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))
            else:
                f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))
        suburbans = [o for o in objects
                     if o.xpath('type[text() = "дом" or text() = "коттедж"]')]
        if len(suburbans):
            root = etree.Element('suburbian')
            for sale in suburbans:
                try:
                    to_cian_suburbans(root, from_bn_suburbans(sale, l))
                except EmptyResult:
                    pass
            if len(flats_rooms_sales) or len(flats_rooms_rents):
                f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))
            else:
                f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8'))

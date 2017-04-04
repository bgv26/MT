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

IN_FILE = 'bncat.xml'
IN_FILE_COMMERCE = 'bncat_comnedv_for_bn.xml'

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


def convert(root_node, item, log):
    try:
        # common part
        description = get_node_value(item, 'description/full')
        ad_id = get_node_value(item, 'id', True)

        if is_block(description):
            raise BlockedRecordException('Blocked: bad description "{}" in advert id [{}]'.format(description, ad_id))

        obj_type = get_node_value(item, 'type')
        action = get_node_value(item, 'action')
        agent_phone = get_node_value(item, 'agent/phone', True)

        lot = etree.SubElement(root_node, 'object')

        # ExternalId - Id объявления
        external_id = etree.SubElement(lot, 'ExternalId')
        external_id.text = gen_new_id(ad_id)

        # Description - Текст объявления
        office = OFFICES[agent_phone]['office']
        lot_number = get_lot_number(ad_id)
        description = etree.SubElement(lot, 'Description')
        description.text = "{}\nПри звонке в {} укажите лот: {}".format(description, office, lot_number)

        # Address - Адрес объявления
        address = etree.SubElement(lot, 'Address')
        address.text = get_node_value(item, 'location/address', True)

        # Phones - Телефон
        phone_schema = etree.SubElement(etree.SubElement(lot, 'Phones'), 'PhoneSchema')
        country_code = etree.SubElement(phone_schema, 'CountryCode')
        country_code.text = '+7'
        phone_number = etree.SubElement(phone_schema, 'Number')
        phone_number.text = OFFICES[agent_phone]['phone']

        # Photos - Фотографии объекта
        photos = etree.SubElement(lot, 'Photos')
        for photo in item.xpath('files/image'):
            photo_schema = etree.SubElement(photos, 'PhotoSchema')
            photo_url = etree.SubElement(photo_schema, 'FullUrl')
            photo_url.text = photo.text
            is_default = etree.SubElement(photo_schema, 'IsDefault')
            is_default.text = 'true'

        # Квартира
        if obj_type == 'квартира':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'flatRent'
            if action == 'продажа':
                category.text = 'flatSale'

            # FlatRoomsCount - Количество комнат
            rooms_count = etree.SubElement(lot, 'FlatRoomsCount')
            rooms_count.text = get_node_value(item, 'rooms-total', True)

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # FloorNumber - Этаж
            floor_number = etree.SubElement(lot, 'FloorNumber')
            floor_number.text = get_node_value(item, 'floor', True)

            # LivingArea - Жилая площадь
            area_living = get_node_value(item, 'living/value')
            if area_living:
                living_area = etree.SubElement(lot, 'LivingArea')
                living_area.text = area_living

            # KitchenArea - Площадь кухни
            area_kitchen = get_node_value(item, 'kitchen/value')
            if area_kitchen:
                kitchen_area = etree.SubElement(lot, 'KitchenArea')
                kitchen_area.text = area_kitchen

            # FloorsCount - Количество этажей в здании
            floors_count = etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount')
            floors_count.text = get_node_value(item, 'floors', True)

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Комната
        if obj_type == 'комната':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'roomRent'
            if action == 'продажа':
                category.text = 'roomSale'

            # RoomsForSaleCount - Количество комнат в продажу/аренду
            rooms_for_sale = etree.SubElement(lot, 'RoomsForSaleCount')
            rooms_for_sale.text = get_node_value(item, 'rooms-offer', True)

            # RoomArea - Площадь комнаты
            area_living = get_node_value(item, 'living/value')
            if area_living:
                living_area = etree.SubElement(lot, 'RoomArea')
                living_area.text = area_living

            # RoomsCount - Количество комнат всего
            rooms_count = etree.SubElement(lot, 'RoomsCount')
            rooms_count.text = get_node_value(item, 'rooms-total', True)

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # FloorNumber - Этаж
            floor_number = etree.SubElement(lot, 'FloorNumber')
            floor_number.text = get_node_value(item, 'floor', True)

            # KitchenArea - Площадь кухни
            area_kitchen = get_node_value(item, 'kitchen/value')
            if area_kitchen:
                kitchen_area = etree.SubElement(lot, 'KitchenArea')
                kitchen_area.text = area_kitchen

            # FloorsCount - Количество этажей в здании
            floors_count = etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount')
            floors_count.text = get_node_value(item, 'floors', True)

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Дом
        if obj_type == 'дом':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'houseRent'
            if action == 'продажа':
                category.text = 'houseSale'

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(item, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            floors_count = get_node_value(item, 'floors')
            build_year = get_node_value(item, 'building/year')
            if floors_count or build_year:
                building = etree.SubElement(lot, 'Building')
                if floors_count:
                    etree.SubElement(building, 'FloorsCount').text = floors_count
                if build_year:
                    etree.SubElement(building, 'BuildYear').text = build_year

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Коттедж
        if obj_type == 'коттедж':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'cottageRent'
            if action == 'продажа':
                category.text = 'cottageSale'

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(item, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            floors_count = get_node_value(item, 'floors')
            build_year = get_node_value(item, 'building/year')
            if floors_count or build_year:
                building = etree.SubElement(lot, 'Building')
                if floors_count:
                    etree.SubElement(building, 'FloorsCount').text = floors_count
                if build_year:
                    etree.SubElement(building, 'BuildYear').text = build_year

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Таунхаус
        if obj_type == 'таунхаус':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'townhouseRent'
            if action == 'продажа':
                category.text = 'townhouseSale'

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(item, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            floors_count = get_node_value(item, 'floors')
            build_year = get_node_value(item, 'building/year')
            if floors_count or build_year:
                building = etree.SubElement(lot, 'Building')
                if floors_count:
                    etree.SubElement(building, 'FloorsCount').text = floors_count
                if build_year:
                    etree.SubElement(building, 'BuildYear').text = build_year

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Участок
        if obj_type == 'участок':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'landSale'

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(item, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(item, 'price/value', True)) * 0.95)

        # Офис
        if obj_type == 'офисы':
            # Category - Категория объявления
            category = etree.SubElement(lot, 'Category')
            if action == 'аренда':
                category.text = 'officeRent'
            if action == 'продажа':
                category.text = 'officeSale'

            # TotalArea - Общая площадь
            total_area = etree.SubElement(lot, 'TotalArea')
            total_area.text = get_node_value(item, 'total/value', True)

            # FloorNumber - Этаж
            floor_number = etree.SubElement(lot, 'FloorNumber')
            floor_number.text = get_node_value(item, 'floor', True)

            # FloorsCount - Количество этажей в здании
            floors_count = etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount')
            floors_count.text = get_node_value(item, 'floors', True)

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = get_node_value(item, 'price/value', True)

    except (EmptyRequiredFieldException, BlockedRecordException, EmptyResult) as e:
        log.write(str(e) + '\n')
        raise EmptyResult()


for cat in DIRECTORIES:
    with open(os.path.join(cat, OUT_FILE), 'w+', encoding='utf-8') as f, \
            open(os.path.join(cat, LOG_FILE), 'w+', encoding='utf-8') as l:
        doc = etree.parse(os.path.join(cat, IN_FILE))
        objects = doc.xpath('bn-object')
        root = etree.Element('feed')
        version = etree.SubElement(root, 'feed_version')
        version.text = '2'
        for obj in objects:
            try:
                convert(root, obj, l)
            except EmptyResult:
                pass
        doc = etree.parse(os.path.join(cat, IN_FILE_COMMERCE))
        objects = doc.xpath('bn-object')
        for obj in objects:
            try:
                convert(root, obj, l)
            except EmptyResult:
                pass
        f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))

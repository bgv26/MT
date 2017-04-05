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
    '8(863)2-417-423': {'office': 'ДОНМТ офис Батайск', 'phone': '9281879795'},
}

SPECIALITIES = {
    'ресторан': 'restaurant',
    'гостиниц': 'hotel',
    'автосервис/мойка': 'carService',
    'бытовое обслуживание': 'domesticServices',
}

COMMERCE = (
    'офисы',
    'торговые помещения',
    'земельные участки',
    'помещения для сферы услуг',
    'производственно-складские помещения',
)

ACTIONS = {
    'аренда': 'Rent',
    'продажа': 'Sale',
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


def get_speciality(text):
    for spec in SPECIALITIES:
        if spec in text:
            return SPECIALITIES[spec]
    return 'other'


def get_category(category, action='', sub_description=''):
    categories = {
        'квартира': 'flat',
        'комната': 'room',
        'дом': 'house',
        'коттедж': 'cottage',
        'таунхаус': 'townhouse',
        'участок': 'landSale',
        'офисы': 'office',
        'торговые помещения': 'shoppingArea',
        'земельные участки': 'commercialLand',
        'помещения для сферы услуг': 'freeAppointmentObject',
    }

    sub_categories = {
        'склад': 'warehouse',
        'производство': 'industry',
    }

    if category in categories:
        if action:
            return categories[category] + ACTIONS[action]
        else:
            return categories[category]
    for sub_category in sub_categories:
        if sub_category in sub_description:
            return sub_categories[sub_category] + ACTIONS[action]


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


def convert(root_node, bn_lot, log):
    try:
        # common part
        bn_description_full = get_node_value(bn_lot, 'description/full')
        bn_id = get_node_value(bn_lot, 'id', True)

        if is_block(bn_description_full):
            raise BlockedRecordException(
                'Blocked: bad description "{}" in advert id [{}]'.format(bn_description_full, bn_id))

        bn_type = get_node_value(bn_lot, 'type')
        bn_action = get_node_value(bn_lot, 'action')
        bn_phone = get_node_value(bn_lot, 'agent/phone', True)

        if bn_phone not in OFFICES:
            raise BlockedRecordException(
                'Blocked: unknown phone number "{}" in advert id [{}]'.format(bn_phone, bn_id))

        lot = etree.SubElement(root_node, 'object')

        # ExternalId - Id объявления
        etree.SubElement(lot, 'ExternalId').text = gen_new_id(bn_id)

        # Description - Текст объявления
        office = OFFICES[bn_phone]['office']
        lot_number = get_lot_number(bn_id)
        etree.SubElement(lot, 'Description').text = \
            "{}\nПри звонке в {} укажите лот: {}".format(bn_description_full, office, lot_number)

        # Address - Адрес объявления
        etree.SubElement(lot, 'Address').text = get_node_value(bn_lot, 'location/address', True)

        # Phones - Телефон
        phone_schema = etree.SubElement(etree.SubElement(lot, 'Phones'), 'PhoneSchema')
        etree.SubElement(phone_schema, 'CountryCode').text = '+7'
        etree.SubElement(phone_schema, 'Number').text = OFFICES[bn_phone]['phone']

        # Photos - Фотографии объекта
        photos = etree.SubElement(lot, 'Photos')
        for photo in bn_lot.xpath('files/image'):
            photo_schema = etree.SubElement(photos, 'PhotoSchema')
            etree.SubElement(photo_schema, 'FullUrl').text = photo.text
            etree.SubElement(photo_schema, 'IsDefault').text = 'true'

        # Квартира
        if bn_type == 'квартира':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'flat' + ACTIONS[bn_action]

            # FlatRoomsCount - Количество комнат
            etree.SubElement(lot, 'FlatRoomsCount').text = get_node_value(bn_lot, 'rooms-total', True)

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # LivingArea - Жилая площадь
            bn_living_area = get_node_value(bn_lot, 'living/value')
            if bn_living_area:
                etree.SubElement(lot, 'LivingArea').text = bn_living_area

            # KitchenArea - Площадь кухни
            bn_kitchen_area = get_node_value(bn_lot, 'kitchen/value')
            if bn_kitchen_area:
                etree.SubElement(lot, 'KitchenArea').text = bn_kitchen_area

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

            # Price - Цена
            bargain = etree.SubElement(lot, 'BargainTerms')
            etree.SubElement(bargain, 'Price').text = str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)
            if bn_action == 'продажа':
                etree.SubElement(bargain, 'MortgageAllowed').text = str(is_mortgage(bn_lot)).lower()

        # Комната
        if bn_type == 'комната':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'room' + ACTIONS[bn_action]

            # RoomsForSaleCount - Количество комнат в продажу/аренду
            etree.SubElement(lot, 'RoomsForSaleCount').text = get_node_value(bn_lot, 'rooms-offer', True)

            # RoomArea - Площадь комнаты
            bn_living_area = get_node_value(bn_lot, 'living/value')
            if bn_living_area:
                etree.SubElement(lot, 'RoomArea').text = bn_living_area

            # RoomsCount - Количество комнат всего
            etree.SubElement(lot, 'RoomsCount').text = get_node_value(bn_lot, 'rooms-total', True)

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # KitchenArea - Площадь кухни
            bn_kitchen_area = get_node_value(bn_lot, 'kitchen/value')
            if bn_kitchen_area:
                etree.SubElement(lot, 'KitchenArea').text = bn_kitchen_area

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)

        # Дом
        if bn_type == 'дом':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'house' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            bn_floors = get_node_value(bn_lot, 'floors')
            bn_build_year = get_node_value(bn_lot, 'building/year')
            if bn_floors or bn_build_year:
                building = etree.SubElement(lot, 'Building')
                if bn_floors:
                    etree.SubElement(building, 'FloorsCount').text = bn_floors
                if bn_build_year:
                    etree.SubElement(building, 'BuildYear').text = bn_build_year

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)

        # Коттедж
        if bn_type == 'коттедж':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'cottage' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            bn_floors = get_node_value(bn_lot, 'floors')
            bn_build_year = get_node_value(bn_lot, 'building/year')
            if bn_floors or bn_build_year:
                building = etree.SubElement(lot, 'Building')
                if bn_floors:
                    etree.SubElement(building, 'FloorsCount').text = bn_floors
                if bn_build_year:
                    etree.SubElement(building, 'BuildYear').text = bn_build_year

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)

        # Таунхаус
        if bn_type == 'таунхаус':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'townhouse' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            bn_floors = get_node_value(bn_lot, 'floors')
            bn_build_year = get_node_value(bn_lot, 'building/year')
            if bn_floors or bn_build_year:
                building = etree.SubElement(lot, 'Building')
                if bn_floors:
                    etree.SubElement(building, 'FloorsCount').text = bn_floors
                if bn_build_year:
                    etree.SubElement(building, 'BuildYear').text = bn_build_year

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)

        # Участок
        if bn_type == 'участок':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'landSale'

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Price - Цена
            price = etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price')
            price.text = str(int(get_node_value(bn_lot, 'price/value', True)) * 0.95)

        # Офис
        if bn_type == 'офисы':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'office' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                get_node_value(bn_lot, 'price/value', True)

        # Торговая площадь
        if bn_type == 'торговые помещения':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'shoppingArea' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                get_node_value(bn_lot, 'price/value', True)

        # Коммерческая земля
        if bn_type == 'земельные участки':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'commercialLand' + ACTIONS[bn_action]

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True)
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'
            if 'поселений' in bn_description_full:
                status = 'settlements'
            elif 'с/х назн.' in bn_description_full:
                status = 'forAgriculturalPurposes'
            else:
                status = 'industryTransportCommunications'
            etree.SubElement(land, 'Status').text = status

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                get_node_value(bn_lot, 'price/value', True)

        bn_description_print = get_node_value(bn_lot, 'description/print')

        # Помещение свободного назначения
        if bn_type == 'помещения для сферы услуг':
            # Category - Категория объявления
            etree.SubElement(lot, 'Category').text = 'freeAppointmentObject' + ACTIONS[bn_action]

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # Specialty - Возможное назначение
            speciality = etree.SubElement(lot, 'Specialty')
            etree.SubElement(etree.SubElement(speciality, 'Types'), 'String').text = get_speciality(
                bn_description_print)

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

            # Price - Цена
            etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                get_node_value(bn_lot, 'price/value', True)

        if bn_type == 'производственно-складские помещения':
            # Склад
            if 'склад' in bn_description_print:
                # Category - Категория объявления
                etree.SubElement(lot, 'Category').text = 'warehouse' + ACTIONS[bn_action]

                # TotalArea - Общая площадь
                etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

                # FloorNumber - Этаж
                etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

                # FloorsCount - Количество этажей в здании
                etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                    get_node_value(bn_lot, 'floors', True)

                # Price - Цена
                etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                    get_node_value(bn_lot, 'price/value', True)

            # Производство
            if 'производство' in bn_description_print:
                # Category - Категория объявления
                etree.SubElement(lot, 'Category').text = 'industry' + ACTIONS[bn_action]

                # TotalArea - Общая площадь
                etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True)

                # FloorNumber - Этаж
                etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

                # FloorsCount - Количество этажей в здании
                etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                    get_node_value(bn_lot, 'floors', True)

                # Price - Цена
                etree.SubElement(etree.SubElement(lot, 'BargainTerms'), 'Price').text = \
                    get_node_value(bn_lot, 'price/value', True)

    except (EmptyRequiredFieldException, BlockedRecordException, EmptyResult) as e:
        log.write(str(e) + '\n')
        raise EmptyResult()


for cat in DIRECTORIES:
    with open(os.path.join(cat, OUT_FILE), 'w+', encoding='utf-8') as f, \
            open(os.path.join(cat, LOG_FILE), 'w+', encoding='utf-8') as l:
        doc = etree.parse(os.path.join(cat, IN_FILE))
        start_time = dt.now()
        objects = doc.xpath('bn-object')
        l.write('+{}+\n'.format('-' * 78))
        l.write('|{:^78}|\n'.format('Start at: {}'.format(start_time.isoformat())))
        l.write('+{}+\n'.format('-' * 78))
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
        current_time = dt.now()
        l.write('+{}+\n'.format('-' * 78))
        l.write('|{:^78}|\n'.format('Finish at: {}'.format(current_time.isoformat())))
        l.write('|{:^78}|\n'.format('Script work for: {} sec'.format((current_time - start_time) / 1000)))
        l.write('+{}+\n'.format('-' * 78))

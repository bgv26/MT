#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from lxml import etree
from config import DIRECTORIES, IN_FILE, IN_FILE_COMMERCE, LOG_FILE, OUT_FILE, ID_PREFIX, BLOCK_PHRASES, OFFICES


class BlockedRecordException(Exception):
    pass


class EmptyRequiredFieldException(Exception):
    pass


class EmptyResult(Exception):
    count = 0


class EmptyField:
    count = 0


def gen_new_id(offer_id):
    return ID_PREFIX + offer_id[4:]


def is_block(text):
    for block in BLOCK_PHRASES:
        if block in text:
            return True
    return False


def get_node_value(parent, node, required=False, field_name=''):
    try:
        value = parent.xpath(node).pop().text.strip()
        return value
    except IndexError:
        if required:
            if not field_name:
                field_name = node
            ad_id = get_node_value(parent, 'id', True)
            raise EmptyRequiredFieldException(
                'Blocked: empty required field "{}" in advert id [{}].\n'.format(field_name, ad_id))
        return ''


def get_speciality(text):
    specialities = {
        'ресторан': 'restaurant',
        'гостиниц': 'hotel',
        'автосервис/мойка': 'carService',
        'бытовое обслуживание': 'domesticServices',
    }

    for spec in specialities:
        if spec in text:
            return specialities[spec]
    return 'other'


def create_category(node, category, action, description):
    actions = {
        'аренда': 'Rent',
        'продажа': 'Sale',
    }

    categories = {
        'квартира': 'flat',
        'комната': 'room',
        'дом': 'house',
        'коттедж': 'cottage',
        'таунхаус': 'townhouse',
        'участок': 'land',
        'офисы': 'office',
        'торговые помещения': 'shoppingArea',
        'земельные участки': 'commercialLand',
        'помещения для сферы услуг': 'freeAppointmentObject',
    }

    sub_categories = {
        'склад': 'warehouse',
        'производство': 'industry',
    }

    if category == 'участок' and action == 'аренда':
        raise BlockedRecordException('Land cannot be in rent.\n')

    if category in categories:
        etree.SubElement(node, 'Category').text = categories[category] + actions[action]
        return
    if category == 'производственно-складские помещения':
        for category in sub_categories:
            if category in description:
                etree.SubElement(node, 'Category').text = sub_categories[category] + actions[action]
                return
    raise BlockedRecordException('Unknown object type "{}".\n'.format(category))


def create_price(node, lot, category, action, price):
    def is_mortgage(item):
        ad_terms = get_node_value(item, 'additional-terms')
        if ad_terms:
            return ad_terms == 'Ипотека'
        return False

    commerce_type = (
        'офисы',
        'торговые помещения',
        'земельные участки',
        'помещения для сферы услуг',
        'производственно-складские помещения',
    )

    ratio = 0.95

    bargain = etree.SubElement(node, 'BargainTerms')
    etree.SubElement(bargain, 'Price').text = price if category in commerce_type else str(int(price) * ratio)
    etree.SubElement(bargain, 'Currency').text = 'rur'
    if action == 'продажа' and (category not in commerce_type and category != 'участок'):
        etree.SubElement(bargain, 'MortgageAllowed').text = str(is_mortgage(lot)).lower()


def get_office_suffix(offer_id):
    return bytes([int(offer_id[9:])]).decode('cp1251')


def get_lot_number(offer_id):
    # symbols from 4 length 5 + char value from three last digits in text
    return offer_id[4:9] + get_office_suffix(offer_id)


def convert(root_node, bn_lot, log):
    err_str = 'Fix this: field "{}" in advert id: [{}] is  empty.\n'

    try:
        # common part
        bn_id = get_node_value(bn_lot, 'id', True)
        bn_type = get_node_value(bn_lot, 'type', True)
        bn_action = get_node_value(bn_lot, 'action', True)
        bn_description_print = get_node_value(bn_lot, 'description/print', True, 'short description')
        bn_description_full = get_node_value(bn_lot, 'description/full', True, 'full description')
        bn_price = get_node_value(bn_lot, 'price/value', True, 'price')

        if is_block(bn_description_full):
            raise BlockedRecordException(
                'Blocked: bad description "{}" in advert id [{}].\n'.format(bn_description_full, bn_id))

        bn_phone = get_node_value(bn_lot, 'agent/phone', True)

        if bn_phone not in OFFICES:
            raise BlockedRecordException(
                'Blocked: unknown phone number "{}" in advert id [{}].\n'.format(bn_phone, bn_id))

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
        bn_photos = bn_lot.xpath('files/image')
        if bn_photos:
            photos = etree.SubElement(lot, 'Photos')
            for photo in bn_photos:
                photo_schema = etree.SubElement(photos, 'PhotoSchema')
                etree.SubElement(photo_schema, 'FullUrl').text = photo.text
                etree.SubElement(photo_schema, 'IsDefault').text = 'true'
        else:
            EmptyField.count += 1
            log.write(err_str.format('photos', bn_id))

        # Category - Категория объявления
        create_category(lot, bn_type, bn_action, bn_description_print)

        # Price - Цена
        create_price(lot, bn_lot, bn_type, bn_action, bn_price)

        # Квартира
        if bn_type == 'квартира':
            # FlatRoomsCount - Количество комнат
            etree.SubElement(lot, 'FlatRoomsCount').text = get_node_value(bn_lot, 'rooms-total', True)

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # LivingArea - Жилая площадь
            bn_living_area = get_node_value(bn_lot, 'living/value')
            if bn_living_area:
                etree.SubElement(lot, 'LivingArea').text = bn_living_area
            else:
                EmptyField.count += 1
                log.write(err_str.format('living area', bn_id))

            # KitchenArea - Площадь кухни
            bn_kitchen_area = get_node_value(bn_lot, 'kitchen/value')
            if bn_kitchen_area:
                etree.SubElement(lot, 'KitchenArea').text = bn_kitchen_area
            else:
                EmptyField.count += 1
                log.write(err_str.format('kitchen area', bn_id))

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

            # BalconiesCount или LoggiasCount - Наличие балкона или лоджии
            bn_balcony = get_node_value(bn_lot, 'balcony')
            if bn_balcony == 'балкон':
                etree.SubElement(lot, 'BalconiesCount').text = '1'
            if bn_balcony == 'лоджия':
                etree.SubElement(lot, 'LoggiasCount').text = '1'

            # SeparateWcsCount или CombinedWcsCount - Наличие раздельного или совмещенного санузла
            if 'санузел раздельный' in bn_description_full:
                etree.SubElement(lot, 'SeparateWcsCount').text = '1'
            if 'санузел совмещенный' in bn_description_full:
                etree.SubElement(lot, 'CombinedWcsCount').text = '1'

        # Комната
        if bn_type == 'комната':
            # RoomsForSaleCount - Количество комнат в продажу/аренду
            bn_rooms_offer = get_node_value(bn_lot, 'rooms-offer')
            if bn_rooms_offer:
                etree.SubElement(lot, 'RoomsForSaleCount').text = bn_rooms_offer
            else:
                EmptyField.count += 1
                log.write(err_str.format('rooms offer', bn_id))

            # RoomArea - Площадь комнаты
            etree.SubElement(lot, 'RoomArea').text = get_node_value(bn_lot, 'living/value', True, 'living area')

            # RoomsCount - Количество комнат всего
            bn_rooms_total = get_node_value(bn_lot, 'rooms-total')
            if bn_rooms_total:
                etree.SubElement(lot, 'RoomsCount').text = bn_rooms_total
            else:
                EmptyField.count += 1
                log.write(err_str.format('rooms total', bn_id))

            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # KitchenArea - Площадь кухни
            bn_kitchen_area = get_node_value(bn_lot, 'kitchen/value')
            if bn_kitchen_area:
                etree.SubElement(lot, 'KitchenArea').text = bn_kitchen_area
            else:
                EmptyField.count += 1
                log.write(err_str.format('kitchen area', bn_id))

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

            # BalconiesCount или LoggiasCount - Наличие балкона или лоджии
            bn_balcony = get_node_value(bn_lot, 'balcony')
            if bn_balcony == 'балкон':
                etree.SubElement(lot, 'BalconiesCount').text = '1'
            if bn_balcony == 'лоджия':
                etree.SubElement(lot, 'LoggiasCount').text = '1'

            # SeparateWcsCount или CombinedWcsCount - Наличие раздельного или совмещенного санузла
            if 'санузел раздельный' in bn_description_full:
                etree.SubElement(lot, 'SeparateWcsCount').text = '1'
            if 'санузел совмещенный' in bn_description_full:
                etree.SubElement(lot, 'CombinedWcsCount').text = '1'

        # Дом, коттедж или таунхаус
        if bn_type == 'дом' or bn_type == 'коттедж' or bn_type == 'таунхаус':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True, 'land area')
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

            # Building - Информация о здании
            bn_floors = get_node_value(bn_lot, 'floors')
            bn_build_year = get_node_value(bn_lot, 'building/year')
            if bn_floors or bn_build_year:
                building = etree.SubElement(lot, 'Building')
                if bn_floors:
                    etree.SubElement(building, 'FloorsCount').text = bn_floors
                else:
                    EmptyField.count += 1
                    log.write(err_str.format('floors', bn_id))
                if bn_build_year:
                    etree.SubElement(building, 'BuildYear').text = bn_build_year
                else:
                    EmptyField.count += 1
                    log.write(err_str.format('building year', bn_id))

            # WcLocationType - Расположение санузла
            if 'санузел в доме' in bn_description_full:
                etree.SubElement(lot, 'WcLocationType').text = 'indoors'
            if 'санузел во дворе' in bn_description_full:
                etree.SubElement(lot, 'WcLocationType').text = 'outdoors'

        # Участок
        if bn_type == 'участок':
            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True, 'land area')
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'

        # Офис
        if bn_type == 'офисы':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

        # Торговая площадь
        if bn_type == 'торговые помещения':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

        # Коммерческая земля
        if bn_type == 'земельные участки':
            # Land - Информация об участке
            land = etree.SubElement(lot, 'Land')
            etree.SubElement(land, 'Area').text = get_node_value(bn_lot, 'lot/value', True, 'land area')
            etree.SubElement(land, 'AreaUnitType').text = 'sotka'
            if 'поселений' in bn_description_full:
                status = 'settlements'
            elif 'с/х назн.' in bn_description_full:
                status = 'forAgriculturalPurposes'
            else:
                status = 'industryTransportCommunications'
            etree.SubElement(land, 'Status').text = status

        # Помещение свободного назначения
        if bn_type == 'помещения для сферы услуг':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # Specialty - Возможное назначение
            speciality = etree.SubElement(lot, 'Specialty')
            etree.SubElement(etree.SubElement(speciality, 'Types'), 'String').text = get_speciality(
                bn_description_print)

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

        if bn_type == 'производственно-складские помещения':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            bn_floors = get_node_value(bn_lot, 'floors', True)
            building = etree.SubElement(lot, 'Building')
            etree.SubElement(building, 'FloorsCount').text = bn_floors

            # PassengerLiftsCount - Наличие пассажирского лифта
            if int(bn_floors) >= 6:
                etree.SubElement(building, 'PassengerLiftsCount').text = '1'

    except (EmptyRequiredFieldException, BlockedRecordException) as e:
        log.write(str(e))
        EmptyResult.count += 1
        raise EmptyResult()


def run():
    for cat in DIRECTORIES:
        with open(os.path.join(cat, LOG_FILE), 'w+', encoding='utf-8') as l:
            start_time = dt.now()
            l.write('+{}+\n'.format('-' * 78))
            l.write('|{:^78}|\n'.format('Start at: {}'.format(start_time.isoformat())))
            l.write('+{}+\n'.format('-' * 78))

            EmptyField.count = 0
            EmptyResult.count = 0

            try:
                doc = etree.parse(os.path.join(cat, IN_FILE))
                objects = doc.xpath('bn-object')
            except IOError:
                objects = []

            total = len(objects)

            root = etree.Element('feed')
            version = etree.SubElement(root, 'feed_version')
            version.text = '2'
            for obj in objects:
                try:
                    convert(root, obj, l)
                except EmptyResult:
                    pass

            try:
                doc = etree.parse(os.path.join(cat, IN_FILE_COMMERCE))
                objects = doc.xpath('bn-object')
            except IOError:
                objects = []

            total += len(objects)

            for obj in objects:
                try:
                    convert(root, obj, l)
                except EmptyResult:
                    pass

            if total:
                with open(os.path.join(cat, OUT_FILE), 'w+', encoding='utf-8') as f:
                    f.write(etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8'))

            exec_time = 'Script execution time: {} sec'
            conclusion = 'Totally parsed: {} offers. Blocked: {}. Must be corrected: {}'

            current_time = dt.now()
            l.write('+{}+\n'.format('-' * 78))
            l.write('|{:^78}|\n'.format('Finish at: {}'.format(current_time.isoformat())))
            l.write('|{:^78}|\n'.format(exec_time.format((current_time - start_time).total_seconds())))
            l.write('|{:^78}|\n'.format(conclusion.format(total, EmptyResult.count, EmptyField.count)))
            l.write('+{}+\n'.format('-' * 78))


if __name__ == '__main__':
    run()

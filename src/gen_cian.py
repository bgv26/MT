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


class Offer:
    blocked_error_string = 'Blocked: {} "{}" in advert id [{}].\n'
    fix_error_string = 'Fix this: field "{}" in advert id: [{}] is  empty.\n'
    ACTIONS = {
        'аренда': 'Rent',
        'продажа': 'Sale',
    }

    def __init__(self, bn_lot, root, log):
        self.bn_lot = bn_lot
        self.root = root
        self.log = log
        self.bn_id = self.get_node_value('id', True)
        self.__description = self.get_node_value('description/full', True, 'full description')

        # check for occurrences block phrases in description
        for block in BLOCK_PHRASES:
            if block in self.__description:
                raise BlockedRecordException(
                    self.blocked_error_string.format('bad description', self.__description, self.bn_id))

        phone = self.get_node_value('agent/phone', True)
        if phone in OFFICES:
            self.__phone = OFFICES[phone]['phone']
            self.__office = OFFICES[phone]['office']
        else:
            raise BlockedRecordException(
                self.blocked_error_string.format('unknown phone number', phone, self.bn_id))

    def get_node_value(self, node, required=False, field_name=''):
        try:
            return self.bn_lot.xpath(node).pop().text.strip()
        except IndexError:
            if required:
                field_name = field_name or node
                raise EmptyRequiredFieldException(
                    self.blocked_error_string.format('empty required field', field_name, self.bn_id))

    def get_node_multiple_values(self, node, required=False, field_name=''):
        result = []
        for item in self.bn_lot.xpath(node):
            result.append(item.text.strip())
        if required and not result:
            field_name = field_name or node
            raise EmptyRequiredFieldException(
                self.blocked_error_string.format('empty required field', field_name, self.bn_id))
        return result

    def get_id(self):
        # ExternalId - Id объявления
        return ID_PREFIX + self.bn_id[4:]

    def get_address(self):
        # Address - Адрес объявления
        return self.get_node_value('location/address', True)

    def get_photos(self):
        # Photos - Фотографии объекта
        bn_photos = self.get_node_multiple_values('files/image')
        if bn_photos:
            return bn_photos
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('photos', self.bn_id))

    def get_description(self):
        # Description - Текст объявления

        # symbols from 4 length 5 + '-8' + char value from three last digits in text
        lot_number = self.bn_id[4:9] + '-8' + bytes([int(self.bn_id[9:])]).decode('cp1251')

        return "{}\nПри звонке в {} укажите лот: {}".format(self.__description, self.__office, lot_number)

    def get_price(self):
        price = self.get_node_value('price/value', True, 'price')
        return str(int(price) * 0.95)


class CommerceOffer(Offer):
    def get_price(self):
        return self.get_node_value('price/value', True, 'price')


class Flat(Offer):
    # Квартира
    def __init__(self, bn_lot, root, log):
        super(Flat, self).__init__(bn_lot, root, log)
        action = self.get_node_value('action', True)
        self.__category = 'flat' + self.ACTIONS[action]

    def __get_flat_rooms_count(self):
        # FlatRoomsCount - Количество комнат
        return self.get_node_value('rooms-total', True)

    def __get_total_area(self):
        # TotalArea - Общая площадь
        return self.get_node_value('total/value', True, 'total area')

    def __get_floor_number(self):
        # FloorNumber - Этаж
        return self.get_node_value('floor', True)

    def __get_living_area(self):
        # LivingArea - Жилая площадь
        bn_living_area = self.get_node_value('living/value')
        if bn_living_area:
            return bn_living_area
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('living area', self.bn_id))

    def __get_kitchen_area(self):
        # KitchenArea - Площадь кухни
        bn_kitchen_area = self.get_node_value('kitchen/value')
        if bn_kitchen_area:
            return bn_kitchen_area
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('kitchen area', self.bn_id))

    def __get_floors_count(self):
        # FloorsCount - Количество этажей в здании
        return self.get_node_value('floors', True)


class Room(Offer):
    # Комната
    def __init__(self, bn_lot, root, log):
        super(Room, self).__init__(bn_lot, root, log)
        action = self.get_node_value('action', True)
        self.__category = 'room' + self.ACTIONS[action]

    def __get_rooms_for_sale_count(self):
        # RoomsForSaleCount - Количество комнат в продажу/аренду
        bn_rooms_offer = self.get_node_value('rooms-offer')
        if bn_rooms_offer:
            return bn_rooms_offer
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('rooms offer', self.bn_id))

    def __get_room_area(self):
        # RoomArea - Площадь комнаты
        return self.get_node_value('living/value', True, 'living area')

    def __get_rooms_count(self):
        # RoomsCount - Количество комнат всего
        bn_rooms_total = self.get_node_value('rooms-total')
        if bn_rooms_total:
            return bn_rooms_total
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('rooms total', self.bn_id))

    def __get_total_area(self):
        # TotalArea - Общая площадь
        return self.get_node_value('total/value', True, 'total area')

    def __get_floor_number(self):
        # FloorNumber - Этаж
        return self.get_node_value('floor', True)

    def __get_kitchen_area(self):
        # KitchenArea - Площадь кухни
        bn_kitchen_area = self.get_node_value('kitchen/value')
        if bn_kitchen_area:
            return bn_kitchen_area
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('kitchen area', self.bn_id))

    def __get_floors_count(self):
        # FloorsCount - Количество этажей в здании
        return self.get_node_value('floors', True)


class House(Offer):
    # Дом
    def __init__(self, bn_lot, root, log):
        super(House, self).__init__(bn_lot, root, log)
        action = self.get_node_value('action', True)
        self.__category = 'house' + self.ACTIONS[action]

    def __get_total_area(self):
        # TotalArea - Общая площадь
        return self.get_node_value('total/value', True, 'total area')

    def __get_land_area(self):
        # Land - Информация об участке
        return self.get_node_value('lot/value', True, 'land area')

    def __get_floors_count(self):
        # FloorsCount - Количество этажей в здании
        bn_floors_count = self.get_node_value('floors')
        if bn_floors_count:
            return bn_floors_count
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('floors', self.bn_id))

    def __get_build_year(self):
        # BuildYear - Год постройки
        bn_build_year = self.get_node_value('building/year')
        if bn_build_year:
            return bn_build_year
        else:
            EmptyField.count += 1
            self.log.write(self.fix_error_string.format('building year', self.bn_id))


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
    # symbols from 4 length 5 + '-8' + char value from three last digits in text
    return offer_id[4:9] + '-8' + get_office_suffix(offer_id)


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
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

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
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

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
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

        # Торговая площадь
        if bn_type == 'торговые помещения':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

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
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

        if bn_type == 'производственно-складские помещения':
            # TotalArea - Общая площадь
            etree.SubElement(lot, 'TotalArea').text = get_node_value(bn_lot, 'total/value', True, 'total area')

            # FloorNumber - Этаж
            etree.SubElement(lot, 'FloorNumber').text = get_node_value(bn_lot, 'floor', True)

            # FloorsCount - Количество этажей в здании
            etree.SubElement(etree.SubElement(lot, 'Building'), 'FloorsCount').text = \
                get_node_value(bn_lot, 'floors', True)

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

            EmptyResult.count = 0
            EmptyField.count = 0

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

import xml.etree.ElementTree as ET
import os

button_type_elements = ['Passive', 'Undefined']  # These Type elements indicates absence of hotkey

unit_elements = {'CUnit': ['parent','default','id',
                           {'CardLayouts': ['CardId', 'index', 'removed',
                                            {'LayoutButtons': ['Face', 'Type', 'Column', 'Row', 'index', 'SubmenuCardId', 'removed',
                                                               {'Face': 'value',
                                                                'Type': 'value',
                                                                'Column': 'value',
                                                                'Row': 'value',
                                                                'index': 'value',
                                                                'SubmenuCardId': 'value',
                                                                'removed': 'value',
                                                                'ShowInGlossary': 'value'}]}],
                           'HotkeyCategory': 'value',
                           'HotkeyAlias': 'value',
                           'GlossaryAlias': 'value',
                           'Description': 'value',
                           'Mob': 'value',
                           'SubgroupAlias': 'value',
                           'SelectAlias': 'value',
                           'Race': 'value'}]}

button_elements = {'CButton': ['parent','default','id',
                               {'Hotkey': 'value',
                                'HotkeySet': 'value',
                                'Name': 'value',
                                'HotkeyAlias': 'value',
                                'Universal': 'value',
                                'Tooltip': 'value'}]}


def find_all(name, path):  # for looking through directory for filename
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def spot_for(elem_path):  # quick function for finding source of different elements
    for path in find_all('UnitData.xml', 'dataimport'):
        root = ET.parse(path).getroot()
        for unit in root.findall("./CUnit"):
            for elem in unit.findall(elem_path):
                print(path, unit.get('id'), elem.tag, elem.attrib)

    for path in find_all('ButtonData.xml', 'dataimport'):
        root = ET.parse(path).getroot()
        for button in root.findall("./CButton"):
            for elem in button.findall(elem_path):
                print(path, button.get('id'), elem.tag, elem.attrib)

# spot_for(".//ShowInGlossary")


def att_iter(elem, elem_dict):
    if elem.attrib:
        for att in elem.attrib:
            if att not in elem_dict:
                elem_dict[att] = [elem.get(att)]
            elif elem.get(att) not in elem_dict[att]:
                elem_dict[att].append(elem.get(att))


def child_iter(elem, elem_dict):
    att_iter(elem, elem_dict[0])
    if list(elem):
        for child in elem:
            if child.tag not in elem_dict[1]:
                elem_dict[1][child.tag] = [{}, {}]
                print(elem.tag, '>>', child.tag)

            child_iter(child,elem_dict[1][child.tag])


def elem_write(elem, scope, file):
    if type(elem) is list:
        if all(isinstance(child, (list, dict)) for child in elem):
            for num in range(len(elem)):
                elem_write(elem[num], scope, file)
        else:
            file.write(' : ["'+'", "'.join(elem)+'"]')
    elif type(elem) is dict:
        for child in elem:
            file.write('\n'+'    '*scope + child)
            elem_write(elem[child], scope + 1, file)


def update_dict():
    unit = [{}, {}]
    for path in find_all('UnitData.xml','dataimport'):
        root = ET.parse(path).getroot()
        child_iter(root, unit)

    with open('unit_dict.txt','w') as f:
        elem_write(unit, 0, f)

    button = [{}, {}]
    for path in find_all('ButtonData.xml','dataimport'):
        root = ET.parse(path).getroot()
        child_iter(root, button)

    with open('button_dict.txt','w') as f:
        elem_write(button,0,f)


# TODO: blacklist+whitelist : is this unit in the players hand yes/no/maybe?
# use .get(key,default=None) to shorten code
# test iterfind(), findtext(), .text
# much repeating, make function iterate over relevant fields ('Cardlayouts', 'HotkeyAlias', 'HotkeyCategory')
# try to find field for SubmenuCardId/CardLayouts/HotkeyAlias ingame name

# def unit_hotkey_extract(path):
#     root = ET.parse(path).getroot()
#     for unit in root.findall('./CUnit'):
#         print(unit.get('id'))
#         if unit.findall('./CardLayouts') is not None:
#             for card in unit.findall('./CardLayouts'):
#                 if 'CardId' in card.attrib:
#                     print('    CardLayouts: ', card.get('CardId'))
#                 else:
#                     print('    CardLayouts: ', 'NO ID')
#                 if card.findall('./LayoutButtons') is not None:
#                     for button in card.findall('./LayoutButtons'):
#                         if button.attrib:
#                             attrib_list = {}
#                             for att in button.attrib:
#                                 if (att == 'Type' and (button.get(att) in button_type_elements)) or (att != 'Type' and att in button_attrib):
#                                     attrib_list[att] = button.get(att)
#                             print('        ', attrib_list)
#                         if list(button):
#                             attrib_list = {}
#                             for att in button:
#                                 if (att.tag == 'Type' and (att.get('value') in button_type_elements)) or (att.tag != 'Type' and (att.tag in button_attrib)):
#                                     attrib_list[att.tag] = att.get('value')
#                             print('        ', attrib_list)
#
#         # for elem in unit_elements
#         if unit.findall('./HotkeyAlias') is not None:
#             for alias in unit.findall('./HotkeyAlias'):
#                 if alias.get('value') is not None:
#                     print('    HotkeyAlias: ', alias.get('value'))
#
#         if unit.findall('./HotkeyCategory') is not None:
#             for cat in unit.findall('./HotkeyCategory'):
#                 if cat.get('value') is not None:
#                     print('    HotkeyCategory: ', cat.get('value'))
#         # TODO: if HotkeyCategory="" + HotkeyAlias="Unit/Category/ZergUnits:"
#             #   HotkeyCategory=HotkeyAlias
#         # if unit.findall('./Mob') is not None:
#         #     for cat in unit.findall('./HotkeyCategory'):
#         #         if cat.get('value') is not None:
#         #             print('    HotkeyCategory: ', cat.get('value'))


# unit_hotkey_extract('dataimport/liberty/UnitData.xml')


# TODO: figure out how data should be saved, so the two functions below can be made for that purpose
def att_iter_restrict(elem, elem_dict, dict_path):
    if elem.attrib:
        for att in elem.attrib:
            if att not in elem_dict:
                elem_dict[att] = [elem.get(att)]
            elif elem.get(att) not in elem_dict[att]:
                elem_dict[att].append(elem.get(att))


def child_iter_restrict(elem, elem_dict, sought_elements):
    att_iter_restrict(elem, elem_dict[0])
    if list(elem):
        for child in elem:
            if child.tag not in elem_dict[1] and child.tag in sought_elements:
                elem_dict[1][child.tag] = [{}, {}]
                print(elem.tag, '>>', child.tag)

            child_iter_restrict(child,elem_dict[1][child.tag])

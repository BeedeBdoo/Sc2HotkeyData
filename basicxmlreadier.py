import xml.etree.ElementTree as ET
import os

# TODO read DocumentInfo files for dependencies
# TODO CardLayouts removed="1", skip these?
# TODO CardLayouts index="", what is it?
# TODO CardLayouts RowText="", what is it?
# TODO LayoutButtons Type="Undefined", skip these?
# TODO LayoutButtons Row="" Column="" stacking
# TODO LayoutButtons Requirement="", mutually exclusive requirements

button_type_elements = ['Undefined']  # These Type elements indicates absence of hotkey

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


# TODO: blacklist+whitelist : is this unit in the players hand yes/no/maybe?
#   if HotkeyCategory="" + HotkeyAlias="Unit/Category/ZergUnits:"
#       HotkeyCategory=HotkeyAlias
# try to find field for SubmenuCardId/CardLayouts/HotkeyAlias ingame name

def get_GameHotkeys(filepath, gamehotkey_dict):
    # for looking through GameHotkeys.txt.
    # Returns a dictionary with hotkey name as index, value as key
    with open(filepath) as file:
        game_hotkeys = file.readlines()
    for line in game_hotkeys:
        if 'Button/Hotkey/' in line and all(not line.split('=')[0].endswith(x) for x in ['_SC1','_NRS','_USD','_USDL']):
            hotkey = line.split('Button/Hotkey/')[-1].split('\n')[0].split('=')
            if hotkey[0] in gamehotkey_dict and gamehotkey_dict[hotkey[0]] != hotkey[-1]:
                print('default overwritten '+filepath+' '+hotkey[0]+' from '+gamehotkey_dict[hotkey[0]]+' to '+hotkey[-1])
            gamehotkey_dict[hotkey[0]] = hotkey[-1]
    return gamehotkey_dict


def get_ButtonData(filepath, uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict):
    root = ET.parse(filepath).getroot()
    for button in root.findall('./CButton[@id]'):
        if 'parent' in button.attrib:
            if button.get('parent') in uni_dict:
                uni_dict[button.get('id')] = uni_dict[button.get('parent')]
            if button.get('parent') in hotkey_dict:
                hotkey_dict[button.get('id')] = hotkey_dict[button.get('parent')]
            else:
                hotkey_dict[button.get('id')] = button.get('parent')
            if button.get('parent') in hotkeyalias_dict:
                hotkeyalias_dict[button.get('id')] = hotkeyalias_dict[button.get('parent')]
            else:
                hotkeyalias_dict[button.get('id')] = button.get('parent')
            if button.get('parent') in hotkeyset_dict:
                hotkeyset_dict[button.get('id')] = hotkeyset_dict[button.get('parent')]

        for child in button.findall('./Universal'):
            uni_dict[button.get('id')] = bool(child.get('value'))
        for child in button.findall('./Hotkey'):
            hotkey_dict[button.get('id')] = child.get('value').split('/')[-1]
        for child in button.findall('./HotkeyAlias'):
            hotkeyalias_dict[button.get('id')] = child.get('value')
        for child in button.findall('./HotkeySet'):
            hotkeyset_dict[button.get('id')] = child.get('value')
    return uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict


def get_UnitData(filepath, gamehotkey_dict, uni_dict, hotkeyalias_dict, subgroupalias_dict, subgrouppriority_dict):
    keylist = []
    conflictsset = {}

    root = ET.parse(filepath).getroot()
    for unit in root.findall('./CUnit'):
        buttonid = ""
        unitid = ""
        # default removes inheriting from older versions?
        if 'parent' in unit.attrib:
            if unit.get('parent') in subgroupalias_dict:
                subgroupalias_dict[unit.get('id')] = subgroupalias_dict[unit.get('parent')]
            if unit.get('parent') in subgroupalias_dict:
                subgrouppriority_dict[unit.get('id')] = subgrouppriority_dict[unit.get('parent')]
        else:
            if unit.get('id') not in subgroupalias_dict:
                subgroupalias_dict[unit.get('id')] = '##id##'
            if unit.get('id') not in subgrouppriority_dict:
                subgrouppriority_dict[unit.get('id')] = "0"

        for child in unit.findall('./SubgroupAlias'):
            subgroupalias_dict[unit.get('id')] = child.get('value')
        for child in unit.findall('./SubgroupPriority'):
            subgrouppriority_dict[unit.get('id')] = child.get('value')

        if subgroupalias_dict[unit.get('id')] == '##id##':
            unitid = unit.get('id')
        elif subgroupalias_dict[unit.get('id')] in subgrouppriority_dict:
            unitid = subgroupalias_dict[unit.get('id')]
        # what if neither?

        for card in unit.findall('./CardLayouts'):
            if unit.get('id') in subgrouppriority_dict and unitid in subgrouppriority_dict and \
                    subgrouppriority_dict[unit.get('id')] != subgrouppriority_dict[unitid]:
                cardid = unit.get('id')
            else:
                cardid = unitid
            if card.get('CardId'):
                cardid += ' - '+card.get('CardId')

            if cardid not in conflictsset:
                conflictsset[cardid] = []
            for button in card.findall('./LayoutButtons'):
                buttonhotkey = "="
                if 'Face' in button.attrib:
                    buttonid = button.get('Face')
                elif list(button):
                    for att in button.findall('./Face'):
                        buttonid = att.get('value')
                elif button.get('removed') == "1" or button.find('./removed').get('value') == "1":
                    continue
                else:
                    print("Error: Missing face on "+unit.get('id')+" in "+filepath)
                    break

                if buttonid in hotkeyalias_dict:
                    buttonid = hotkeyalias_dict[buttonid]

                if buttonid in gamehotkey_dict:
                    buttonhotkey += gamehotkey_dict[buttonid]

                if buttonid in uni_dict and uni_dict[buttonid]:
                    if buttonid not in conflictsset[cardid]:
                        conflictsset[cardid].append(buttonid)
                    if buttonid+buttonhotkey not in keylist:
                        keylist.append(buttonid+buttonhotkey)
                else:
                    if buttonid+'/'+unitid not in conflictsset[cardid]:
                        conflictsset[cardid].append(buttonid+'/'+unitid)
                    if buttonid+'/'+unitid+buttonhotkey not in keylist:
                        keylist.append(buttonid+'/'+unitid+buttonhotkey)
    return keylist, conflictsset, subgroupalias_dict, subgrouppriority_dict


def unit_hotkey_extract(path_unit, path_button):
    gamehotkey_dict = get_GameHotkeys('dataimport/core/GameHotkeys.txt', {})
    gamehotkey_dict = get_GameHotkeys('dataimport/liberty/GameHotkeys.txt', gamehotkey_dict)

    uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict = get_ButtonData('dataimport/core/ButtonData.xml', {}, {}, {}, {})
    uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict = get_ButtonData('dataimport/liberty/ButtonData.xml', uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict)

    for hotkey in hotkey_dict:
        if hotkey_dict[hotkey] in gamehotkey_dict:
            gamehotkey_dict[hotkey] = gamehotkey_dict[hotkey_dict[hotkey]]
        else:
            print('error: '+str(hotkey_dict[hotkey])+', Hotkey for '+str(hotkey)+' expected but not found in GameHotkeys.')

    keylist, conflictsset, subgroupalias_dict, subgrouppriority_dict = get_UnitData('dataimport/core/UnitData.xml', gamehotkey_dict, uni_dict, hotkeyalias_dict, {}, {})
    return get_UnitData('dataimport/liberty/UnitData.xml', gamehotkey_dict, uni_dict, hotkeyalias_dict, subgroupalias_dict, subgrouppriority_dict)

# "for elem in unit_elements"
# if unit.findall('./HotkeyAlias') is not None:
#     for alias in unit.findall('./HotkeyAlias'):
#         if alias.get('value') is not None:
#             print('    HotkeyAlias: ', alias.get('value'))

# if unit.findall('./HotkeyCategory') is not None:
#     for cat in unit.findall('./HotkeyCategory'):
#         if cat.get('value') is not None:
#             print('    HotkeyCategory: ', cat.get('value'))


def key_extractor():
    with open('defaults (from TheCoreConverter).txt') as file:
        data = file.readlines()
        keylist, conflictsset, subgroupalias_dict, subgrouppriority_dict = unit_hotkey_extract('dataimport/liberty/UnitData.xml', 'dataimport/liberty/ButtonData.xml')
        with open('generated defaults list.txt','w') as f:
            for line in sorted(keylist):
                f.write(line+'\n')
                if all(line not in dataline for dataline in data):
                    print('line missing in TheCoreConverter '+line)
        with open('generated conflicts checks.txt','w') as f:
            for conflicts in sorted(conflictsset):
                f.write(conflicts+': '+', '.join(conflictsset[conflicts])+'\n')


key_extractor()

# quick check on inconsistent defaults
# gamehotkey_dict = {}
# for filepath in find_all('GameHotkeys.txt','dataimport'):
#     get_GameHotkeys(filepath, gamehotkey_dict)
#
# for filepath in find_all('UnitData.xml','dataimport'):
#     root = ET.parse(filepath).getroot()
#     for unit in root.findall('./CUnit[@default]'):
#         print(filepath,unit.get('id'))
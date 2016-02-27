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

def unit_hotkey_extract(path_unit,path_button):
    keylist = []
    unibuttons = []
    aliasbuttons = {}
    hotkeylist = {}
    conflictsset = {}

    with open('dataimport/liberty/GameHotkeys.txt') as f:
        hotkeys = f.readlines()
    for line in hotkeys:
        if 'Button/Hotkey/' in line and all(not line.split('=')[0].endswith(x) for x in ['_SC1','_NRS','_USD','_USDL']):
            hotkey = line.split('Button/Hotkey/')[-1].split('\n')[0].split('=')
            if hotkey[0] not in hotkeylist:
                hotkeylist[hotkey[0]] = hotkey[1]

    for buttonpath in ['dataimport/core/ButtonData.xml',path_button]:
        root = ET.parse(buttonpath).getroot()
        for button in root.findall('./CButton[@id]'):
            if 'parent' in button.attrib:
                if button.get('parent') in unibuttons and button.get('id') not in unibuttons:
                    unibuttons.append(button.get('id'))
                if button.get('parent') in aliasbuttons and button.get('id') not in aliasbuttons:
                    aliasbuttons[button.get('id')] = aliasbuttons[button.get('parent')]
                else:
                    aliasbuttons[button.get('id')] = button.get('parent')
            if button.get('id') not in unibuttons:
                for unielem in button.findall('./Universal'):
                    if unielem.get('value') == "1" and button.get('id') not in unibuttons:
                        unibuttons.append(button.get('id'))
            for alias in button.findall('.HotkeyAlias'):
                if alias.get('value') and button.get('id') not in aliasbuttons:
                    aliasbuttons[button.get('id')] = alias.get('value')
                elif aliasbuttons[button.get('id')] != alias.get('value'):
                    print('alias overwrite :'+button.get('id')+':'+alias.get('value')+'!='+aliasbuttons[button.get('id')])

    root = ET.parse(path_unit).getroot()
    for unit in root.findall('./CUnit'):
        unitid = unit.get('id')
        buttonid = ""
        if unit.findall('SubgroupAlias'):
            for subgroupalias in unit.findall('SubgroupAlias'):
                unitid = subgroupalias.get('value')
        if unit.findall('./CardLayouts'):
            for card in unit.findall('./CardLayouts'):
                if card.findall('./LayoutButtons'):
                    if card.get('CardId'):
                        cardid += ' - '+card.get('CardId')
                    else:
                        cardid = ""
                    conflictsset[unitid+cardid] = []
                    for button in card.findall('./LayoutButtons'):
                        if button.get('Type') == 'Passive' or any(att.get('value') == 'Passive' for att in button):
                            break
                        buttonhotkey = ""
                        if 'Face' in button.attrib:
                            buttonid = button.get('Face')
                        elif list(button):
                            for att in button.findall('./Face'):
                                buttonid = att.get('value')

                        if buttonid in aliasbuttons:
                            buttonid = aliasbuttons[buttonid]

                        if buttonid in hotkeylist:
                            buttonhotkey = '='+hotkeylist[buttonid]

                        if buttonid in unibuttons:
                            if buttonid not in conflictsset[unitid+cardid]:
                                conflictsset[unitid+cardid].append(buttonid)
                            if buttonid+buttonhotkey not in keylist:
                                keylist.append(buttonid+buttonhotkey)
                        else:
                            if buttonid+'/'+unitid not in conflictsset[unitid+cardid]:
                                conflictsset[unitid+cardid].append(buttonid+'/'+unitid)
                            if buttonid+'/'+unitid+buttonhotkey not in keylist:
                                keylist.append(buttonid+'/'+unitid+buttonhotkey)

                        if buttonhotkey == "":
                            print(button.get('Type'))
                            print(any(att.get('value') == 'Passive' for att in button))
                            print(buttonid)
    return keylist,conflictsset

# "for elem in unit_elements"
# if unit.findall('./HotkeyAlias') is not None:
#     for alias in unit.findall('./HotkeyAlias'):
#         if alias.get('value') is not None:
#             print('    HotkeyAlias: ', alias.get('value'))

# if unit.findall('./HotkeyCategory') is not None:
#     for cat in unit.findall('./HotkeyCategory'):
#         if cat.get('value') is not None:
#             print('    HotkeyCategory: ', cat.get('value'))
# TODO: if HotkeyCategory="" + HotkeyAlias="Unit/Category/ZergUnits:"
    #   HotkeyCategory=HotkeyAlias

with open('defaults.txt') as file:
    data = file.readlines()
    keylist,conflictsset = unit_hotkey_extract('dataimport/liberty/UnitData.xml', 'dataimport/liberty/ButtonData.xml')
    with open('keylist_test.txt','w') as f:
        for line in sorted(keylist):
            f.write(line+'\n')
            if all(line not in dataline for dataline in data):
                print(line)
    with open('conflict_test.txt','w') as f:
        for conflicts in sorted(conflictsset):
            f.write(conflicts+': '+', '.join(conflictsset[conflicts])+'\n')



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

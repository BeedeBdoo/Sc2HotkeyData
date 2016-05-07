# reads xml trees for UnitData.xml and ButtonData.xml to create conflict checks and list default hotkeys

import xml.etree.ElementTree as ET
import os
import copy
import xml_tree_merger

# TODO CardLayouts RowText="", what is it? - Low Priority
# TODO LayoutButtons Row="" Column="" stacking
# TODO LayoutButtons Requirement="", mutually exclusive requirements

# following CUnit children might be interesting for determining if unit is accesible by players
# HotkeyCategory, HotkeyAlias, GlossaryAlias, Mob, Race
#
# Untested: relation between HotkeyCategory and HotkeyAlias:
# if HotkeyCategory == "" and HotkeyAlias="Unit/Category/ZergUnits":
#     HotkeyCategory = HotkeyAlias

# dependencies read from dependencies window in Sc2GalaxyEditor
dependencies = [
    ['core', 'liberty', 'challenges'],
    ['core', 'liberty', 'libertymulti'],
    ['core', 'liberty', 'swarm', 'swarmmulti'],
    ['core', 'liberty', 'swarm', 'void', 'voidmulti'],
    ['core', 'liberty', 'libertycampaign', 'libertystory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'swarmstory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'voidstory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'voidprologue'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'alliedcommanders'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'novastoryassets'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'campaigncommon'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'campaigncommon', 'novastoryassets', 'novacampaign']]

unit_path_lists = []; button_path_lists = []; hotkey_path_lists = []
for journey in dependencies:
    unit_path_lists.append(['data/'+path+'/UnitData.xml' for path in journey])
    button_path_lists.append(['data/'+path+'/ButtonData.xml' for path in journey])
    hotkey_path_lists.append(['data/'+path+'/GameHotkeys.txt' for path in journey])


def find_all(name, path):  # for looking through directory for filename
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def get_GameHotkeys(filepath, gamehotkey_dict):
    # looks through GameHotkeys.txt file
    # returns a dictionary with hotkey name as index, value as key
    if not os.path.isfile(filepath):
        return gamehotkey_dict
    with open(filepath) as file:
        game_hotkeys = file.readlines()
    for line in game_hotkeys:
        if 'Button/Hotkey/' in line and all(not line.split('=')[0].endswith(x) for x in ['_SC1','_NRS','_USD','_USDL']):
            hotkey = line.split('Button/Hotkey/')[-1].split('\n')[0].split('=')
            if hotkey[0] in gamehotkey_dict and gamehotkey_dict[hotkey[0]] != hotkey[-1]:
                print('default overwritten '+filepath+' '+hotkey[0]+' from '+gamehotkey_dict[hotkey[0]]+' to '+hotkey[-1])
            gamehotkey_dict[hotkey[0]] = hotkey[-1]
    return gamehotkey_dict


def get_ButtonData(tree):
    uni_dict = {}; hotkey_dict = {}; hotkeyalias_dict = {}; hotkeyset_dict = {}
    root = tree.getroot()
    for button in root.getchildren():
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


def get_UnitData(tree, gamehotkey_dict, uni_dict, hotkeyalias_dict):
    root = tree.getroot()

    keylist = []
    conflictsset = {}

    subgroupalias_dict = {}
    subgrouppriority_dict = {}
    for unit in root.getchildren():
        subgroupalias = unit.find('./SubgroupAlias')
        subgrouppriority = unit.find('./SubgroupPriority')
        subgroupalias_dict[unit.get('id')] = subgroupalias.get('value')
        if subgrouppriority is not None:
            subgrouppriority_dict[unit.get('id')] = subgrouppriority.get('value')

    for unit in root.getchildren():
        unitid = subgroupalias_dict[unit.get('id')]

        for card in unit.findall('./CardLayouts'):
            rowcolumn = {}
            for button in card.findall('./LayoutButtons'):
                if button.get('Face') is None:
                    print("error: no 'Face' attribute found on button-index", button.get('index'),'on',unit.get('id'))
                    continue
                elif button.get('Face') not in hotkeyalias_dict:
                    print('error: button "'+button.get('Face')+'" on "'+unit.get('id')+'" no HotkeyAlias data found')
                    continue
                if button.get('Row')+button.get('Column') in rowcolumn:
                    rowcolumn[button.get('Row')+button.get('Column')].append(button)
                else:
                    rowcolumn[button.get('Row')+button.get('Column')] = [button]

            card_conflicts = [[]]
            for key in sorted(rowcolumn):
                newCC = []
                for sublist in card_conflicts:
                    for button_list in rowcolumn[key]:
                        tmp_sublist = []
                        for elem in sublist:
                            tmp_sublist.append(elem)
                        tmp_sublist.append(button_list)
                        newCC.append(tmp_sublist)
                card_conflicts = newCC

            card_conflicts_id = []
            for num, card_conflict in enumerate(card_conflicts):
                append_cc = [hotkeyalias_dict[button.get('Face')] for button in card_conflict]
                if append_cc not in card_conflicts_id:
                    card_conflicts_id.append(append_cc)
                else:
                    del card_conflicts[num]

            for num, card_conflict in enumerate(card_conflicts_id):
                cardid = unit.get('id')
                if len(unit.findall('./CardLayouts')) > 1:
                    cardid += ' (card index '+str(card.get('index'))+')'
                if len(card_conflicts_id) > 1:
                    cardid += ' (variant '+str(num)+')'

                if cardid in conflictsset:
                    print('error: duplicate cardid', cardid)
                    continue
                conflictsset[cardid] = []
                for buttonid in card_conflict:
                    buttonhotkey = ''
                    if buttonid in gamehotkey_dict:
                        buttonhotkey = gamehotkey_dict[buttonid]

                    if not (buttonid in uni_dict and uni_dict[buttonid]):
                        buttonid += '/'+unitid

                    if buttonid+'='+buttonhotkey not in keylist:
                        keylist.append(buttonid+'='+buttonhotkey)

                    if buttonid not in conflictsset[cardid]:
                        conflictsset[cardid].append(buttonid)
    # clean up conflictsset
    temp_keys = conflictsset.copy()
    for key1 in conflictsset:
        for key2 in conflictsset:
            if (key2 in temp_keys and
                        key1 != key2 and
                    all(keys in conflictsset[key1] for keys in conflictsset[key2])):
                # print (key2+'\t<=\n'+key1+'\n')
                temp_keys.pop(key2, None)
    conflictsset = temp_keys


    # conflictsset_invert = {}
    # for conflict_key in sorted(conflictsset):
    #     if ','.join(sorted(conflictsset[conflict_key])) not in conflictsset_invert and len(conflictsset[conflict_key]) > 1:
    #         conflictsset_invert[','.join(sorted(conflictsset[conflict_key]))] = conflict_key
    # conflictsset = {value: key for key, value in conflictsset_invert.items()}
    return keylist, conflictsset


def write_to_file(keylist, conflictsset):
    with open('defaults (from TheCoreConverter).txt') as file:
        data = file.readlines()
    # write defaults list
    with open('generated defaults list.txt','w') as f:
        for line in sorted(keylist):
            f.write(line+'\n')
            if all(line not in dataline for dataline in data):
                print('line missing in TheCoreConverter '+line)
    # write conflict checks
    # with open('generated conflicts checks.txt', 'w') as f:
    #     for conflicts in sorted(conflictsset):
    #         f.write(conflicts+': '+', '.join(conflictsset[conflicts])+'\n')
    with open('generated conflicts checks.py', 'w') as f:
        f.write("# This file is generated by a script. DO NOT edit.\n\n")
        jlength = len(conflictsset)
        j = 1
        for conflict_key in sorted(conflictsset):
            isfirst = j == 1
            if isfirst:
                prefix = 'CONFLICT_CHECKS = {'
            else:
                prefix = '                   '

            islast = j == jlength
            if islast:
                suffix = '}'
            else:
                suffix = ',\n'
            f.write(prefix + "\'" + conflict_key + "\' : " + str(conflictsset[conflict_key]) + suffix)
            j += 1


def generate_checks(index):
    gamehotkey_dict = {}
    for path in hotkey_path_lists[index]:
        gamehotkey_dict = get_GameHotkeys(path, gamehotkey_dict)

    button_tree = xml_tree_merger.tree_merger(button_path_lists[index])
    unit_tree = xml_tree_merger.tree_merger(unit_path_lists[index])

    button_tree.write('Merged ButtonData.xml')
    unit_tree.write('Merged UnitData.xml')

    uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict = \
        get_ButtonData(button_tree)

    keylist, conflictsset = \
        get_UnitData(unit_tree, gamehotkey_dict, uni_dict, hotkeyalias_dict)

    write_to_file(keylist, conflictsset)
    print('conflicts checks generation complete.')

generate_checks(-1)

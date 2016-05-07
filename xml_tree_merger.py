# Appends Unit/ButtonData.xml files to each other to create a single data file
# also strips the files of irrelevant

import xml.etree.ElementTree as ET
import os
import copy


def tree_remove_empty(tree):
    # for UnitData. removes units without command cards
    root = tree.getroot()
    for root_child in root.getchildren():
        if root_child.tag == 'CUnit' and not any(elem.tag == 'CardLayouts' for elem in root_child.getchildren()):
            root.remove(root_child)
            continue
        # if button 'Type' attribute is "Undefined", the button is hidden and unreachable. basically removed.
        for cardlayout in root_child.findall('./CardLayouts'):
            for button in cardlayout.findall("./LayoutButtons[@Type='Undefined']"):
                # print('tree merger: undefined button "'+str(button.get('Face'))+'"')
                cardlayout.remove(button)


def strip_elem(elem):
    # basic frame has no id. Setting id to 'None'
    elem.set('id', str(elem.get('id')))
    elem.set('parent', str(elem.get('parent')))
    # keep only important children
    for child in elem.getchildren():
        if elem.tag == 'CUnit' and child.tag not in ['CardLayouts', 'SubgroupAlias', 'SubgroupPriority'] \
                or elem.tag == 'CButton' and child.tag not in ['Universal', 'Hotkey', 'HotkeyAlias', 'HotkeySet']:
            elem.remove(child)
        elif child.tag == 'CardLayouts':
            for button in child.getchildren():
                if button.tag != 'LayoutButtons':
                    child.remove(button)
                    continue
                # make all LayoutButton subelements attributes
                for buttonelem in button.getchildren():
                    button.set(buttonelem.tag, buttonelem.get('value'))
                    button.remove(buttonelem)


def apply_parent(elem, parent_elem):
    # add ageindex to determine 'age' of element. 0 being oldest
    ageindex = 0
    for button in parent_elem.findall('.//LayoutButtons'):
        button.set('ageindex', str(ageindex))
        ageindex += 1
    for button in elem.findall('.//LayoutButtons'):
        button.set('ageindex', str(ageindex))
        ageindex += 1
    # add relevant parent elements to elem
    for parentchild in parent_elem.getchildren():
        if parentchild.tag == 'CardLayouts':
            elem.append(copy.deepcopy(parentchild))
        elif elem.find('./'+parentchild.tag) is None:
            # elem does not have child. inherit from parent
            if parentchild.get('value') is None:
                print(parentchild.tag,elem.get('id'),'parented by',parent_elem.get('id'))
            val = parentchild.get('value').replace('##id##', elem.get('id'))
            ET.SubElement(elem, parentchild.tag, value=val)
    # From here on it's special treatment of cardlayouts for CUnits
    if elem.find('./CardLayouts') is None:
        return elem
    # indice cardlayouts.
    cardlayoutindex = 0
    if parent_elem.find('./CardLayouts') is not None:
        cardlayoutindex = max([int(cardlayout.get('index')) for cardlayout in parent_elem.findall('./CardLayouts')]) + 1
    for cardlayout in elem.findall('./CardLayouts'):
        if cardlayout.get('index') is None:
            cardlayout.set('index', str(cardlayoutindex))
            cardlayoutindex += 1
    # merge cardlayouts with same index
    cardlayouts = {}
    for cardlayout in elem.findall('./CardLayouts'):
        if cardlayout.get('index') not in cardlayouts:
            cardlayouts[cardlayout.get('index')] = cardlayout
        else:
            for button in cardlayout:
                cardlayouts[cardlayout.get('index')].append(button)
            elem.remove(cardlayout)
    # remove cardlayouts with 'removed' attrib
    for cardlayout in elem.findall('./CardLayouts'):
        if cardlayout.get('removed') == "1":
            elem.remove(cardlayout)
    # indice layoutbuttons
    for cardlayout in elem.findall('./CardLayouts'):
        buttonindex = 0
        parent_cardlayout = parent_elem.find("./CardLayouts[@index='"+cardlayout.get('index')+"']")
        if parent_cardlayout is not None and parent_cardlayout.find('./LayoutButtons') is not None:
            buttonindex = max([int(button.get('index')) for button in parent_cardlayout.findall('./LayoutButtons')]) + 1
        for button in cardlayout.findall('./LayoutButtons'):
            if button.get('index') is None:
                button.set('index', str(buttonindex))
                buttonindex += 1
    # merge layoutbuttons with same index
    for cardlayout in elem.findall('./CardLayouts'):
        buttons = {}
        for button in cardlayout.findall('./LayoutButtons'):
            if button.get('index') not in buttons:
                buttons[button.get('index')] = button
            elif int(button.get('ageindex')) > int(buttons[button.get('index')].get('ageindex')):
                # this button is newer than button in buttons
                for attribute in button.attrib:
                    buttons[button.get('index')].set(attribute, button.get(attribute))
                cardlayout.remove(button)
            else:
                # this button is older than button in buttons
                for attribute in buttons[button.get('index')].attrib:
                    button.set(attribute, buttons[button.get('index')].get(attribute))
                cardlayout.remove(buttons[button.get('index')])
                buttons[button.get('index')] = button
    # remove buttons with 'removed' attrib
    for cardlayout in elem.findall('./CardLayouts'):
        for button in cardlayout.findall('./LayoutButtons'):
            if button.get('removed') == "1":
                cardlayout.remove(button)


def append_element(elem, tree):
    root = tree.getroot()
    strip_elem(elem)
    # does an elem in tree have same id as elem?
    foreignlist = [child.get('id') == elem.get('id') for child in root]
    if sum(foreignlist) > 1:
        print('error: duplicate id', elem.get('id'))
    elemisforeign = not bool(sum(foreignlist))
    if not elemisforeign and elem.get('parent') == 'None':
        elem.set('parent', elem.get('id'))
    # get parent elem from tree
    parent_elem = None
    for child in root.getchildren():
        if child.get('id') == elem.get('parent'):
            if parent_elem is not None:
                print('error: duplicate id', child.get('id'), 'parent')
            parent_elem = child
    if not elemisforeign and elem.get('parent') != elem.get('id'):
        print('error: forerign element', elem.get('id'), 'has an overwriting parent')

    if parent_elem is None:
        root.append(elem)
        if elem.get('id') != 'None':
            print('error:', elem.get('id'), 'has no parent')
    else:
        apply_parent(elem, parent_elem)
        root.append(elem)
        if elem.get('id') == elem.get('parent'):
            root.remove(parent_elem)
    return tree


def append_tree(tree, newtree):
    root = newtree.getroot()
    for elem in root.getchildren():
        if elem.tag != 'CUnit' and elem.tag != 'CButton':
            root.remove(elem)
            continue
        tree = append_element(elem, tree)
    return tree


def tree_merger(ordered_path_list):
    tree = ET.ElementTree(ET.Element('Catalog', {}))
    print('tree merger: initiated')
    for path in ordered_path_list:
        print('tree merger: append initiated', path)
        tree = append_tree(tree, ET.parse(path))
        print('tree merger: append completed', path)
    tree_remove_empty(tree)
    print('tree merger: compteted')
    return tree

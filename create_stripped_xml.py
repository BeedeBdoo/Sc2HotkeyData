# Strips UnitData.xml and ButtonData.xml of irrelevant data. Possible data structure for saving hotkey data

import xml.etree.ElementTree as ET
import os

def find_all(name, path):  # for looking through directory for filename
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def xml_button_copy(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for root_child in root.findall('./'):
        if root_child.tag != 'CButton':
            root.remove(root_child)
            break
        for child in root_child.findall('./'):
            if child.tag not in ['Universal', 'Hotkey', 'HotkeyAlias', 'HotkeySet']:
                root_child.remove(child)
    tree.write('output.xml')


def xml_unit_copy(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for root_child in root.findall('./'):
        if root_child.tag != 'CUnit':
            root.remove(root_child)
            break
        for child in root_child.findall('./'):
            if child.tag not in ['Cardlayouts']:
                root_child.remove(child)
    tree.write('output.xml')
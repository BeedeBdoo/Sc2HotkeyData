# from an xml file create a mathematical set union of all children, attributes and values in an overly complicated way

import xml.etree.ElementTree as ET
import os


def find_all(name, path):  # for looking through directory for filename
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def att_iter(elem, elem_dict):  # iterates over all atttributes from input element
    if elem.attrib:
        for att in elem.attrib:
            if att not in elem_dict:
                elem_dict[att] = [elem.get(att)]
            elif elem.get(att) not in elem_dict[att]:
                elem_dict[att].append(elem.get(att))


def child_iter(elem, elem_dict):  # iterates over all children from input element
    att_iter(elem, elem_dict[0])
    if list(elem):
        for child in elem:
            if child.tag not in elem_dict[1]:
                elem_dict[1][child.tag] = [{}, {}]
                print(elem.tag, '>>', child.tag)

            child_iter(child,elem_dict[1][child.tag])


def elem_write(elem, scope, file):  # writes out nested dictionary created by child_iter()
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


def update_union():
    unit = [{}, {}]
    for path in find_all('UnitData.xml', 'dataimport'):
        root = ET.parse(path).getroot()
        child_iter(root, unit)

    with open('Unified UnitData.txt','w') as f:
        elem_write(unit, 0, f)

    button = [{}, {}]
    for path in find_all('ButtonData.xml', 'dataimport'):
        root = ET.parse(path).getroot()
        child_iter(root, button)

    with open('Unified ButtonData.txt','w') as f:
        elem_write(button, 0, f)


update_union()
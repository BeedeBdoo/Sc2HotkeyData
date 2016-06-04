# reads xml trees for UnitData.xml and ButtonData.xml to create conflict checks and list default hotkeys

import xml.etree.ElementTree as ET
import os
import copy
from xml_tree_merger import tree_merger
from math import floor
from math import log10
import pickle


# TODO CardLayouts RowText="", what is it? - Low Priority
# TODO LayoutButtons Requirement="", mutually exclusive requirements

# following CUnit children might be interesting for determining if unit is accesible by players
# HotkeyCategory, HotkeyAlias, GlossaryAlias, Mob, Race
#
# Untested: relation between HotkeyCategory and HotkeyAlias:
# if HotkeyCategory == "" and HotkeyAlias="Unit/Category/ZergUnits":
#     HotkeyCategory = HotkeyAlias

# mutually exclusive requirements
# hots sublists contains mutually exclusive items. coop contains mutually exclusive lists
hots_requirements = [['HotSHaveSwarmlingSpawningPool', 'HotSHaveRaptorSpawningPool'],
                     ['HotSHaveSplitterling', 'HaveHotSHunter'],
                     ['HaveRoachCorpser', 'HaveRoachVile'],
                     ['HaveHotSImpaler', 'HaveHotSLurker'],
                     ['HotSHaveSwarmHostSplitA', 'HotSHaveSwarmHostSplitB'],
                     ['HaveHotSMutaliskBroodLord','HaveHotSMutaliskViper'],
                     ['HaveHotSNoxious', 'HaveHotSTorrasque'],
                     ['HaveHotSZerglingFrenzy', 'HaveHotSZerglingHealth', 'HaveHotSMetabolicBoost'],
                     ['HaveHotSBanelingHeal', 'HaveHotSBanelingCorrosiveBile', 'HaveHotSRupture'],
                     ['HaveHotSRoachDamage', 'HaveHotSRoachShield', 'HaveHotSTunnelingClaws'],
                     ['HaveHotSHydraliskHealth', 'HaveHotSGroovedSpines'],
                     ['HaveHotSBurrowSwarmHost', 'HaveHotSRapidIncubation', 'HaveHotSPressurizedGlands'],
                     ['HaveHotSViciousGlaive', 'HaveHotSExplosiveGlaive', 'HaveHotSRapidRegeneration'],
                     ['HaveHotSMonarchBlades', 'HaveHotSBurrowCharge', 'HaveHotSTissueAssimilation'],
                     ['HaveK5ZerglingRespawn', 'HaveK5ImprovedOverlords', 'HaveK5AutoExtractor'],
                     ['HaveK5TwoDrones', 'HaveK5GasBonuses', 'HaveK5CreepBonuses'],
                     ['HaveK5InfestBroodlings', 'HaveK5Fury', 'HaveK5Cooldowns']]

coop_requirements = {'Abathur': ['HotSHaveViper', 'HaveToxicNestDamageGivesMarkforCollectionDebuff', 'HaveViperAbductImprovedStun', 'HaveViperImprovedCastRange', 'HotSHaveDevourer', 'HotSHaveSwarmHost', 'HaveHotSRapidIncubation', 'HaveHotSLocustSpeed', 'HaveGuardian', 'HaveGuardianAttackRangeIncrease', 'HaveHotSBurrowSwarmHost', 'AbathurLevel02', 'AbathurLevel03', 'AbathurLevel04', 'AbathurLevel06', 'AbathurLevel08', 'AbathurLevel09', 'AbathurLevel10', 'AbathurLevel11', 'AbathurLevel12', 'BiomassBuffEmptyVisible', 'BiomassBuffVisible', 'HaveBioMechanicalTransfusionPassive', 'HaveBrutaliskLeviathanSymbiote', 'HaveCorrosiveBileDamageIncrease', 'HaveCorrosiveBileRadiusIncrease', 'HaveDevourerAoEDamage', 'HaveHotSPressurizedGlands', 'HaveOrganicCarapace', 'HaveHotSRoachShield', 'HaveRoachVile', 'HotSHaveInfestor', 'HaveHotSMutaliskViper', 'HaveHotSRoachDamage'],
                     'Artanis': ['HaveBarrier', 'HaveVoidStalkerDragoon', 'HaveReaverIncreasedScarabSplashRadius', 'HaveHighTemplarEnergyUpgradeHighArchon''HaveSOAWarpTech', 'HaveResearchDoubleGravitonBeamPassive', 'HaveHealingPsionicStormHighArchon', 'HaveDragoonHealth', 'HaveSuperiorWarpGates', 'HaveSOAHeroicShield', 'HaveSingularityCharge', 'HaveHealingPsionicStorm', 'HaveHighTemplarEnergyUpgrade', 'HaveReaverIncreasedScarabCount', 'ArtanisLevel02', 'ArtanisLevel04', 'ArtanisLevel05', 'ArtanisLevel06', 'ArtanisLevel07', 'ArtanisLevel08', 'ArtanisLevel09', 'ArtanisLevel10', 'ArtanisLevel11', 'ArtanisLevel12'],
                     'Karax': ['HaveVoidSentryPurifier', 'HaveSOASolarLanceUpgrade', 'HaveSOARepairBeam', 'HaveSentry', 'HaveSolarEfficiencyLevel1', 'HaveKhaydarinMonolith', 'HaveSolarEfficiencyLevel2', 'HaveSOAOrbitalStrikeUpgrade', 'HaveColossus', 'HaveFireBeam', 'HaveVoidColossusFireBeam', 'HaveMiragePhaseArmor', 'HaveCarrierRepairDrones', 'HaveCarrier', 'HaveSOARepairBeamExtraTarget', 'HaveSolarEfficiencyLevel3', 'HaveKaraxEnergyRegenUpgrade', 'HaveKaraxExtendedThermalLance', 'HaveKaraxPhoenixRangeUpgrade', 'HaveKaraxSOAChronoPassive', 'HaveKaraxTurretAttackSpeed', 'HaveKaraxTurretRange', 'KaraxLevel02', 'KaraxLevel04', 'KaraxLevel05', 'KaraxLevel06', 'KaraxLevel07', 'KaraxLevel08', 'KaraxLevel09', 'KaraxLevel10', 'KaraxLevel12', 'KaraxLevel14'],
                     'Kerrigan': ['HaveHotSExplosiveGlaive', 'HaveSeismicSpines', 'HaveHotSHydraliskHealth', 'HaveHotSRapidRegeneration', 'HaveK5Fury', 'HaveMutaliskSunderingGlave', 'HaveHotSChitinousPlating', 'HaveK5Cooldowns', 'HaveHotSMutaliskBroodLord', 'HaveHotSTissueAssimilation', 'HaveK5ChainLightning', 'HaveBroodlordSpeed', 'HaveGroovedSpines', 'HaveHotSViciousGlaive', 'HaveCoopMutalisk', 'HaveKerriganVoidCoopEnergyRegen', 'KerriganLevel02', 'KerriganLevel04', 'KerriganLevel05', 'KerriganLevel06', 'KerriganLevel09', 'KerriganLevel10', 'KerriganLevel11', 'KerriganLevel13', 'KerriganLevel15'],
                     'Raynor': ['HaveFortifiedBunkerCarapace', 'ShrikeTurretResearched', 'HALORocketsResearched', 'HaveNeosteelFrame', 'UseNeoSteelFrame', 'HaveShieldWall', 'HaveImprovedSiegeMode', 'HaveOrbitalDropPods', 'HaveRaynorCommanderHyperionAdvancedTargetingSystems', 'RaynorLevel02', 'RaynorLevel04', 'RaynorLevel05', 'RaynorLevel06', 'RaynorLevel07', 'RaynorLevel09', 'RaynorLevel11', 'RaynorLevel13', 'RaynorLevel15'],
                     'Swann': ['HaveScienceVesselFreeRepairSecondary', 'HailstormMissilePods', 'HaveMaelstromRounds', 'HaveInfernalPreigniter', 'HaveWraithImprovedBurstLaser', 'HaveCycloneLockOnDamageUpgrade', 'HaveTerranDefenseRangeBonus', 'HaveHellbatHellArmor', 'HaveScienceVesselFreeRepair', 'HaveSwannCommander', 'HaveSwannCommanderImmortalityProtocol', 'HaveSwannCommanderKelMorianWorkerCloak', 'HaveSwannKelMorianGrenadeTurretUpgrade', 'HaveSwannTurretIncreasedAttackSpeed', 'SwannLevel02', 'SwannLevel04', 'SwannLevel05', 'SwannLevel07', 'SwannLevel09', 'SwannLevel11', 'SwannLevel13'],
                     'Vorazun': ['HaveSOAAutoAssimilator', 'HaveOracleStasisWardUpgrade', 'HaveDarkArchonFullStartingEnergy', 'HaveSOARecallonDeath', 'HaveStalker', 'HaveVoidRayPrismaticRange', 'HaveVoidStalkerBlinkShieldRestore', 'HaveBlinkShieldRestore', 'HaveCorsairPermanentCloak', 'HaveVorazunCommander', 'VorazunLevel02', 'VorazunLevel04', 'VorazunLevel05', 'VorazunLevel06', 'VorazunLevel09', 'VorazunLevel10', 'VorazunLevel11', 'VorazunLevel12', 'VorazunLevel13'],
                     'Zagara': ['HaveHotSBanelingHeal', 'HaveHotSRupture', 'HotSHaveAberration', 'HaveScourgeGasCostReduction', 'HaveBileLaunchers', 'HaveArtilleryDucts', 'HaveRapidBombardment', 'HaveK5TwoDrones', 'HaveAberrationArmorAura', 'HaveHotSBanelingCorrosiveBile', 'HaveQueenDoubleInjectLarva', 'HaveScourgeSplashDamage', 'HaveZagaraVoidCoopAberrationBanelingIncubation', 'HaveZagaraVoidCoopAttackUpgrade', 'HaveZagaraVoidCoopBanelingSpawner', 'ZagaraHaveCentrificalHooks', 'ZagaraLevel02', 'ZagaraLevel03', 'ZagaraLevel04', 'ZagaraLevel05', 'ZagaraLevel06', 'ZagaraLevel07', 'ZagaraLevel08', 'ZagaraLevel09', 'ZagaraLevel11', 'ZagaraLevel13']}
unsorted_coop_requirements = ['HotSHaveSwarmHostSplitA', 'HotSHaveSwarmHostSplitB', 'HaveLair', 'HavePhoenixRangeUpgrade', 'HaveGenerateCreep', 'HaveGlialReconstitution', 'HaveHotSGroovedSpines', 'HaveHotSMutaliskBroodLordAndHaveGreaterSpire', 'HavePhotonCannon', 'HaveAdeptShadeDebuff', 'NotUnderConstruction', 'GhostPermanentCloak', 'HotSHaveSporeCrawler', 'HaveHotSZerglingHealth', 'HaveHotSZerglingHealth', 'HaveCycloneLockOnAirUpgrade', 'HaveAdeptPiercingAttack', 'HaveRoachCorpser', 'HaveAdvancedConstruction', 'HaveMPAdrenalGlands', 'HaveMPMetabolicBoost', 'HaveHotSMonarchBlades', 'HaveHotSImpaler', 'HaveGraviticBoosters', 'HavePneumatizedCarapace', 'HotSHaveSpineCrawler', 'HaveVoidColossusTaldarim', 'HaveSOAMatrixOverload', 'HaveVoidStalkerBlinkCharges', 'HaveMonitor', 'HotSHaveDefiler', 'UseShapedBlastReq', 'HaveResearchCripplingPsionicStorm', 'HaveCycloneLockOnRangeUpgrade2', 'HaveZerglingArmorShred', 'HaveAdept', 'HaveLiberatorImprovedAARange']

requirements = {'swarmstory': hots_requirements,
                'alliedcommanders': coop_requirements}

# dependencies read from dependencies window in Sc2GalaxyEditor
dependencies = [
    ['core', 'liberty', 'challenges'],
    ['core', 'liberty', 'libertymulti'],
    ['core', 'liberty', 'swarm', 'swarmmulti'],
    ['core', 'liberty', 'swarm', 'void', 'voidmulti'],
    ['core', 'liberty', 'libertycampaign', 'libertystory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'swarmstory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'voidprologue'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'voidstory'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'alliedcommanders'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'novastoryassets'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'campaigncommon'],
    ['core', 'liberty', 'libertycampaign', 'swarm', 'swarmcampaign', 'void', 'voidcampaign', 'campaigncommon', 'novastoryassets', 'novacampaign']]

# tree for loading depencies to avoid loading the same dependencies too many times
depenload = ['core', 'liberty', ['challenges',
                                 'libertymulti',
                                 ['swarm', ['swarmmulti',
                                           ['void', 'voidmulti']]],
                                 'libertycampaign', ['libertystory',
                                                     ['swarm', 'swarmcampaign', ['swarmstory',
                                                                                 'voidprologue',
                                                                                 ['void', 'voidcampaign', ['voidstory',
                                                                                                           'alliedcommanders',
                                                                                                           'novastoryassets'
                                                                                                           'campaigncommon',
                                                                                                           ['novastoryassets', 'campaigncommon', 'novacampaign']]]]]]]]

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
            # if hotkey[0] in gamehotkey_dict and gamehotkey_dict[hotkey[0]] != hotkey[-1]:
            #     print('default overwritten '+filepath+' '+hotkey[0]+' from '+gamehotkey_dict[hotkey[0]]+' to '+hotkey[-1])
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


def get_UnitData(tree, gamehotkey_dict, uni_dict, hotkeyalias_dict, cardid_suffix):
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
            # sort xml button elements in row/column dictionary
            rowcolumn = {}
            for button in card.findall('./LayoutButtons'):
                if button.get('Face') is None:
                    # print("error: no 'Face' attribute found on button-index", button.get('index'),'on',unit.get('id'))
                    continue
                elif button.get('Face') not in hotkeyalias_dict:
                    # print('error: button "'+button.get('Face')+'" on "'+unit.get('id')+'" no HotkeyAlias data found')
                    continue
                if button.get('Row')+button.get('Column') in rowcolumn:
                    rowcolumn[button.get('Row')+button.get('Column')].append(button)
                else:
                    rowcolumn[button.get('Row')+button.get('Column')] = [button]

            # if more buttons share same row/column, use combinatorics
            # to generate all possible layouts depending on what button is active
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

            # go from storing xml button elements to storing buttonids
            card_conflicts_id = []
            for num, card_conflict in enumerate(card_conflicts):
                append_cc = [hotkeyalias_dict[button.get('Face')] for button in card_conflict]

                # coop requirements handling. cardlayouts shouldn't source buttons from different commanders
                if cardid_suffix == 'alliedcommanders':
                    req_vector = [button.get('Requirements') for button in card_conflict if button.get('Requirements') is not None]
                    req_source = {}
                    for commander in coop_requirements:
                        req_source[commander] = [int(req in coop_requirements[commander]) for req in req_vector]
                        if sum(req_source[commander]) == 0:
                            req_source.pop(commander, None)
                    source_commander = ''
                    for commander in req_source:
                        if source_commander in req_source and len(req_source[commander]) > len(req_source[source_commander]):
                            source_commander = commander
                    consistent_commander = True
                    for num, item in enumerate(req_source[source_commander]):
                        if item == 0:
                            if sum([req_source[commander][num] for commander in req_source]) > 0:
                                consistent_commander = False
                                break
                    if not consistent_commander:
                        del card_conflicts[num]
                        break

                if append_cc not in card_conflicts_id:
                    card_conflicts_id.append(append_cc)
                else:
                    del card_conflicts[num]

            for num, card_conflict in enumerate(card_conflicts_id):
                cardid = cardid_suffix+unit.get('id')
                if len(unit.findall('./CardLayouts')) > 1:
                    cardid += ' (card index '+str(card.get('index'))+')'
                if len(card_conflicts_id) > 1:
                    cardid += ' temp variant'+str(num)

                if cardid in conflictsset:
                    print('error: duplicate cardid', cardid)
                    continue
                conflictsset[cardid] = []
                for buttonid in card_conflict:
                    if buttonid in gamehotkey_dict and gamehotkey_dict[buttonid]:
                        buttonhotkey = gamehotkey_dict[buttonid]
                    else:
                        continue

                    if not (buttonid in uni_dict and uni_dict[buttonid]):
                        buttonid += '/'+unitid

                    if buttonid+'='+buttonhotkey not in keylist:
                        keylist.append(buttonid+'='+buttonhotkey)

                    if buttonid not in conflictsset[cardid]:
                        conflictsset[cardid].append(buttonid)

    return sorted(keylist), conflictsset


def write_to_file(keylist, conflictsset, duplicateset):
    # write defaults list
    with open('output/Defaults.ini','w') as f:
        for line in sorted(keylist):
            f.write(line+'\n')
    # write duplicate list
    with open('output/DifferentDefault.ini','w') as f:
        f.write('[Settings]\n\n[Hotkeys]\n\n[Commands]\n')
        for line in sorted(duplicateset):
            f.write(line+'=\n')
    # write conflict checks
    with open('output/ConflictsChecks.py', 'w') as f:
        f.write("# This file is generated by a script.\n\n")
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
            f.write(prefix + "\'" + conflict_key + "\': " + str(conflictsset[conflict_key]) + suffix)
            j += 1


def generate_checks():
    gamehotkey_dict = {}
    keylist = []
    conflictsset = {}
    duplicateset = set()
    keydict = {}
    for index in range(len(dependencies)):
        for path in hotkey_path_lists[index]:
            gamehotkey_dict = get_GameHotkeys(path, gamehotkey_dict)
        path_destination_name = dependencies[index][-1]
        print('merge buttons '+str(index+1)+' of '+str(len(dependencies)))
        button_tree = tree_merger(button_path_lists[index])
        print('merge units '+str(index+1)+' of '+str(len(dependencies)))
        unit_tree = tree_merger(unit_path_lists[index])

        print('get ButtonData '+str(index+1)+' of '+str(len(dependencies)))
        uni_dict, hotkey_dict, hotkeyalias_dict, hotkeyset_dict = \
            get_ButtonData(button_tree)
        print('get UnitData '+str(index+1)+' of '+str(len(dependencies)))
        temp_keylist, temp_conflictsset = \
            get_UnitData(unit_tree, gamehotkey_dict, uni_dict, hotkeyalias_dict, path_destination_name+'/')

        temp_keydict = {key: value for key, value in [item.split('=') for item in temp_keylist]}
        for key in temp_keydict:
            if key in keydict and temp_keydict[key] not in keydict[key].split(', '):
                print(key, keydict[key])
                keydict[key] += ', '+temp_keydict[key]
                print(key, keydict[key])
                duplicateset.add(key)
            elif key not in keydict:
                keydict[key] = temp_keydict[key]
        keylist = [key+'='+keydict[key] for key in keydict]

        # TODO: keylist needs to deal with same-key different defaults across different game modes

        conflictsset = {**conflictsset, **temp_conflictsset}

    # clean up conflictsset
    temp_keys = conflictsset.copy()
    for key1 in conflictsset:
        if key1 in temp_keys:
            if len(temp_keys[key1]) < 1:
                temp_keys.pop(key1, None)
                continue
            for key2 in conflictsset:
                if (key2 in temp_keys and
                            key1 != key2 and
                        all(keys in conflictsset[key1] for keys in conflictsset[key2])):
                    temp_keys.pop(key2, None)
    conflictsset = temp_keys

    # repetetive spagetthi for improving the naming of same-command-card-different-variants
    key_variant = ""
    temp_keys = []
    i = 0
    nmax = len(conflictsset)
    for n, key in enumerate(sorted(conflictsset)):
        if ' temp variant' in key:
            tmpkey = key[:key.index(' temp variant')]
            if len(key_variant) == 0:
                key_variant = tmpkey
                i = 1
                temp_keys.append(key)
            elif tmpkey == key_variant:
                i += 1
                temp_keys.append(key)
            else:
                for num in range(i):
                    temp = conflictsset[temp_keys[num]]
                    del conflictsset[temp_keys[num]]
                    if i == 1:
                        conflictsset[key_variant] = temp
                    else:
                        conflictsset[key_variant+' '+(len(str(i))-len(str(num)))*'0'+str(num)] = temp
                temp_keys = [key]
                i = 1
                key_variant = tmpkey
        elif i != 0:
            for num in range(i):
                temp = conflictsset[temp_keys[num]]
                del conflictsset[temp_keys[num]]
                if i == 1:
                    conflictsset[key_variant] = temp
                else:
                    conflictsset[key_variant+' '+(len(str(i))-len(str(num)))*'0'+str(num)] = temp
            temp_keys = []
            i = 0
            key_variant = ""
        if nmax == n:
            for num in range(i):
                temp = conflictsset[temp_keys[num]]
                del conflictsset[temp_keys[num]]
                if i == 1:
                    conflictsset[key_variant] = temp
                else:
                    conflictsset[key_variant+' '+(len(str(i))-len(str(num)))*'0'+str(num)] = temp


    write_to_file(keylist, conflictsset, duplicateset)
    print('conflicts checks generation complete.')

generate_checks()


def list_all_req():
    requirements = {}
    for path in find_all('UnitData.xml', 'data'):
        requirements[path] = set()
        tree = ET.parse(path)
        root = tree.getroot()
        for button in root.findall('.//LayoutButtons[@Requirements]'):
            requirements[path].add(button.get('Requirements'))
    for path in requirements:
        print(path, requirements[path])

def update_coop_req():
    new_requirements = set()
    path = 'data/alliedcommanders/UnitData.xml'
    tree = ET.parse(path)
    root = tree.getroot()
    for button in root.findall('.//LayoutButtons[@Requirements]'):
        if all(all(button.get('Requirements') not in req for req in coop_requirements[commander]) for commander in coop_requirements) \
                and all(button.get('Requirements') not in req for req in unsorted_coop_requirements):
            new_requirements.add(button.get('Requirements'))
    print(sorted(new_requirements))

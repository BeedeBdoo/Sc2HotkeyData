Updated for Sc2 patch 3.1.1.39948

HotkeyData holds every* relevant command card with the 'abilityname=key' format used in .SC2Hotkeys files, structured like in the ingame hotkey editor, for a specific campaign/multiplayer/gamemode in Sc2.
'key' in 'abilityname=key' is the default value used by that key. 
Additional HotkeyData files can be added for arcade games

Currently uses 2 abbreviations for a group of abilities that often show up in command cards:
BasicUnitCommands: Move=M, Stop=S, MoveHoldPosition=H, MovePatrol=P, Attack=A
PacifistUnitCommands: Move=M, Stop=S, MoveHoldPosition=H, MovePatrol=P

Scripts:
create_command_list.py	: Creates a list of every key found in all HotkeyData files combined
create_conflict_check.py: Creates a list of lists with every unique command card with those who are sub-variations (same but with less keys) of other removed
verify_hotkeydata.py	: Prints out inconsistentcies in what the same ability is bound to in different HotkeyData files


TODO:
tidy up LotV Camp and Coop Zerg Story HotkeyData



*Some might be missing
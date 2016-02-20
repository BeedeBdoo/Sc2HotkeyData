Updated for Sc2 patch 3.1.1.39948

HotkeyData holds (mostly) every elevant command card with the 'abilityname=key' format used in .SC2Hotkeys files, structured like in the ingame hotkey editor, for a specific campaign/multiplayer/gamemode in Sc2.
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


UPDATE: new data under 'dataimport'.

Some loosely used terminology
Button: the squary things you can click on.
Ability: what triggers when buttons are clicked. Not particularly interesting for the purpose of listing hotkeys
Hotkey: keyboard keys that trigger Buttons

Left: XML view									Right: Detailed view
<HotkeyAlias value=""/>	Default: Self			(Basic) UI: CButton HotkeyAlias
	Overwrites the value of a hotkey to that of its Alias
	
<CButton id=""></CButton>						(Basic) UI: CButton Hotkey
	Name of the button. Referenced in .SC2Hotkeys. Note this is not necesarilly the name showing up ingame.
	
<Universal value="1"/>	Default: 0				(Basic) UI: CButton Universal
	If a button is universal, it's key in .SC2Hotkeys will not mention caster
	e.g. 	universal: Stim= , Cancel= , overlordspeed=
		not universal: Charge/Zealot= , Heal/Medivac=

<HotkeySet value=""/>	Default: None			(Basic) UI: CButton HotkeySet
	Buttons with the same HotkeySet value will not conflict.

<CUnit id=""></CUnit>							(Basic) UI: CUnit Name
	Name of unit. Important for non-universal buttons, as they are listed 'CButton id/CUnit id=' in .SC2Hotkeys

<HotkeyCategory value="Unit/Category/..."/>		(Basic) UI: CUnits HotkeyCategory
	'...' can here be values TerranUnits, TerranStory, ProtossUnits, ... , ZergStory. Otherwise the whole value is likely blank.
	Determines where the unit shows up in the ingame hotkey interface. If value is not blank, it'll likely show up in the hotkey-editor ingame, which makes the unit's keys relevant

<LaytoutButtons Face="" Type=""/>
	Element for individual buttons on a unit. Face takes on the 'CButton id' value. Type has a number of different values. "Passive" means the button is passive and can thus be ignored



The purpose of this project is to file StarCraft 2 Hot-keys and Hot-key conflicts for the purpose of creating a 
foundation for checking conflicts and missing keys in custom Hot-key layouts meant to support game-modes outside 
of multiplayer, such as the StarCraft 2 Campaign.
StarCraft 2 ©2016 BLIZZARD ENTERTAINMENT, INC.
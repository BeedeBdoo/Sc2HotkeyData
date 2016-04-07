# manual version
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


# automatic version
Some loosely used terminology
Button: the squary things you can click on.
Ability: what triggers when buttons are clicked.
Hotkey: keyboard keys that trigger buttons. [Hotkeys] in .SC2Hotkeys will be refered to as globals

ButtonData.xml
	CButton attribute 'id' is the one featured as ability in .SC2Hotkeys
	attribute 'parent', all children inherit from parent
	look for following children
		Universal, attribute 'value'. If value="1", UnitId isn't mentioned in the .SC2Hotkey. e.g. "Stim=" or "Stim/Marine="
		HotkeySet, attribute 'value'. Buttons of the same HotkeySet does not conflict. e.g. Cloak and Decloak
		Hotkey, attribute 'value'. Inherited default of this button. e.g. OracleAttack has "Button/Hotkey/Attack", same default hotkey as Attack.
		HotkeyAlias, attribute 'value'. Inherited hotkey of this button. e.g. CancelCocoon has "Button/Hotkey/Attack". CancelCocoon will then ALWAYS have the same hotkey as Cancel.
			
GameHotkeys.txt
	Look for 'Button/Hotkey/...=' (these are [Commands]) and 'UI/Hotkey/...=' (these are [Hotkeys]) lines without any suffixes (_SC1, _NRS, _USD, _USDL)
		e.g. 'Button/Hotkey/250mmStrikeCannons=C', then 250mmStrikeCannons/Thor=C is the .SC2Hotkeys entry
		
UnitData.xml
	CUnit attribue 'id' is one featured as caster in .SC2Hotkeys
	attribute 'parent', all children inherit from parent
	look for child CardLayouts and its attributes 'index', 'CardId and 'removed'. Its children
		LayoutButtons and their attributes/children (they can be either)
			index
			Face
			Type
			Row
			Column

										--- Button data ---
<CButton id="" parent="">...</CButton>												Detailed view name: (Basic) UI: CButton Hotkey
	Element for containing buttons
	id: Name of the button. Referenced in .SC2Hotkeys. Reference to ingame name given by GameStrings.txt
	parent: this button will inherit all data in parent. Parent referenced by its id. Default: "CButton"

<HotkeyAlias value=""/>																Detailed view name: (Basic) UI: CButton HotkeyAlias
	Overwrites this buttons hotkey to that of the value. Default: own button id
		
<Universal value="1"/>																Detailed view name: (Basic) UI: CButton Universal
	If a button is universal, it's key in .SC2Hotkeys will not mention caster. Default: "0"
	e.g. 	universal: Stim= , Cancel= , overlordspeed=
		not universal: Charge/Zealot= , Heal/Medivac=

<HotkeySet value=""/>		Default: None											Detailed view name: (Basic) UI: CButton HotkeySet
	Buttons with the same HotkeySet value will not conflict.
	
										--- Unit data ---
<CUnit id="" parent="">...</CUnit>													Detailed view name: (Basic) UI: CUnit Name
	Name of unit. Important for non-universal buttons, as they are listed 'CButton id/CUnit id=' in .SC2Hotkeys

<HotkeyCategory value="Unit/Category/..."/>											Detailed view name: (Basic) UI: CUnits HotkeyCategory
	'...' can here be values TerranUnits, TerranStory, ProtossUnits, ... , ZergStory. Otherwise the whole value is likely blank.
	Determines where the unit shows up in the ingame hotkey interface. If value is not blank, it'll likely show up in the hotkey-editor ingame, which makes the unit's keys relevant

<CardLayouts index="", CardId="", removed="1">...	</CardLayouts>
	houses the LayoutButtons. These are effectively command cards.

<LayoutButtons Face="" Type=""/>
	Element for individual buttons on a unit. Face takes on the 'CButton id' value. Type has a number of different values. "Passive" means the button is passive and can thus be ignored

<HotkeyAlias value=""/>		Default: CUnit id										Detailed view name: (Basic) UI: CUnit HotkeyAlias
	Unit id's in value will cause this unit to share it's ingame hotkey section with that unit
	e.g.	Burrowed zerg units suse their unburrowed variant as a HotkeyAlias. 
			Whenever you look at a burrow-able zerg unit in the hotkey editor, 
			the command card will then be accompanied by that of the burrowed variant.

if subgroup alias and subgroup priority are the same, command cards will overlap on union selection

The purpose of this project is to file StarCraft 2 Hot-keys and Hot-key conflicts for the purpose of creating a 
foundation for checking conflicts and missing keys in custom Hot-key layouts meant to support game-modes outside 
of multiplayer, such as the StarCraft 2 Campaign.
StarCraft 2 is a game made by Blizzard Entertainment Inc.
		
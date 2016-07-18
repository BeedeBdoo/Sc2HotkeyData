filepaths = ['data\HotkeyData LotV Multiplayer.txt',
			 'data\HotkeyData Coop.txt',
                         'data\HotkeyData Nova Campaign.txt',
			 'data\HotkeyData LotV Campaign.txt',
			 'data\HotkeyData LotV Prologue.txt',
			 'data\HotkeyData HotS Campaign.txt',
			 'data\HotkeyData WoL Campaign.txt',
			 'data\HotkeyData HotS Multiplayer.txt',
			 'data\HotkeyData WoL Multiplayer.txt',
			 'data\HotkeyData Left2Die.txt']

def make_key_list(filename,key_list):
	#adds to a unique list, key_list, of 'ability=key' lines found in HotkeyData file
	with open(filename,'r') as f:
		for num,full_line in enumerate(f,1):
			line = full_line.strip(' \t\n\r')
			if '=' in line and not line in key_list:
				key_list.append(line)
	return key_list

	
key_list = []
for file in filepaths:
	key_list = make_key_list(file,key_list)

key_list.sort()
with open('Commands.txt','w') as f:
	for key in key_list:
		f.write(key+'\n')


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

def check_unbounds(filename):
	#looks for unbounds in a HotkeyData file
	key_set = set()
	with open(filename,'r') as f:
		for num,fill_line in enumerate(f,1):
			line = fill_line.strip(' \t\n\r')
			if line and line[-1] == '=':
				print(filename,num,line)
				key_set |= {line[:-1]}
	return key_set

def key_extract(filename):
	#Creates a dictionary of all hotkeys in given HotkeyData file
	key_dict = dict()
	with open(filename) as f:
		for unstripped_line in f:
			if '=' in unstripped_line:
				line = unstripped_line.strip(' \t\n\r').split('=')
				key_dict[line[0]] = line[1]
	return key_dict

key_dict = {}
for file in filepaths:
	key_dict.update(key_extract(file))

def verify_datafile(filename,key_dict):
	#fills out unbound keys in given HotkeyData file from what it can
	#keep in mind some defaults are inconsistent and should be ignored from printout
	#inconsistent defaults can be found in subfolder
	with open(filename, 'r') as file:
		data = file.readlines()

	changes_made = 0
	print('---',filename[:-4],'---')
	for num,fill_line in enumerate(data):
		line = fill_line.strip(' \t\n\r')
		if line and '=' in line:
			line_split = line.split('=')
			if line_split[0] in key_dict and key_dict[line_split[0]] != line_split[1]:
				print (num,'\t',line,' =/= ',key_dict[line_split[0]])
			# if line and line[-1] == '=':
				# if line[:-1] in key_dict:
					# data[num] = fill_line.strip('\n\r')+key_dict[line.strip(' \t\n\r')[:-1]]+'\n'
					# changes_made = changes_made + 1
				# else:
					# print(num,line)
	# print('No. edits  : ',changes_made)
	# if changes_made == 0:
		# return

	# with open('Filled ',filename, 'w') as file:
		# file.writelines( data )
	print('\n\n')

for file in filepaths:
	verify_datafile(file,key_dict)

#todo:
#Ignore keys that are default from inconsistent defaults.txt

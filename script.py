conversion_dict = {
            ' Street ':[' St. ',' St '],
            'Street ' : ['St ', 'Opp '],
            ' Road ': [' Rd. ',' Rd '],
            ' Opposite ':[' Opp. ',' Opp '],
            'Opposite':['Opp. ','Opp ']
        }

for key,value in conversion_dict.items():
	for x in value:
		print(x)
import json
import operator

x = json.load(open('ingredients.json','r'))

sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)
for i,xs in enumerate(sorted_x):
	if i > 500:
		break 
	print(xs[0])
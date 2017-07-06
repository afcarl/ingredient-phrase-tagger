import random


foods = open('foods.txt','r').read().split("\n")
measurements = [
	"cup",
	"cups",
	"tbl",
	"tablespoons",
	"tablespoon",
	"tsp",
	"teaspoon",
	"teaspoons",
	"tsp.",
	"tbl.",
	"c.",
	"ounce",
	"oz",
	"ounces",
	"gallon",
	"liter",
	"grams",
	"g",
	"pound",
	"lb",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
]
notes = [
	"canned",
	"dissolved",
	"cooked",
	"roasted",
	"chopped",
	"finely chopped",
	"unflavored",
	"seasoned",
	"melted",
	"minced",
	"blackened",
	"chopped",
	"kosher",
	"dry",
	"crumbs",
	"freshly grated",
	"grated",
	"to taste",
	"freshly squeezed",
	"washed",
	"medium",
	"medium-large",
	"large",
	"small",
	"dissolved in",
	"sifted",
	"recipe follows"
	"raw",
	"see note",
	"available at",
	"granulated",
	"shredded",
	"about",
	"packets",
	"extra large",
	"boiling",
	"peeled",
	"diced",
	"minced or mashed in",
	"a mortar and pestle",
	"fresh",
	"thick",
	"Greek-style",
	"drained",
	"thinly sliced",
	"peeled",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
	"",
]
nums = {
	"1":1,
	"2":2,
	"3":3,
	"4":4,
	"5":5,
	"6":6,
	"7":7,
	"8":8,
	"9":9,
	"":0,
}
fracs = {
	"3/4":0.75,
	"1/2":0.5,
	"1/3":0.3333,
	"2/3":0.6666,
	"1/4":0.25,
	"1/8":0.125,
	"":0,
}

def randomIngredient():
	ing = random.choice(foods)
	num = random.choice(list(nums.keys()))
	frac = random.choice(list(fracs.keys()))
	note = random.choice(notes)
	if random.random() < 0.1:
		note += " " + random.choice(notes)
	if random.random() < 0.1:
		note += " and " + random.choice(notes)
	if random.random() < 0.1:
		note += " or " + random.choice(notes)
	if random.random() < 0.1:
		note += " (" + random.choice(notes) + ")"
	mea = random.choice(measurements)
	comment = note.strip()
	item = ing 
	measure = mea
	r = random.random()
	if random.random() < 0.3:
		ing = "of " + ing
	if random.random() < 0.02:
		ing = "cans " + ing
	text = " ".join("{} {} {} {} {}".format(num,frac,mea,note,ing).split())
	amount = fracs[frac]+nums[num]
	if amount == 0:
		amount = ""
	if random.random() < 0.3:
		note = random.choice(notes)
		text += ", {}".format(note)	
		comment += ", {}".format(note)
	if random.random() < 0.3:
		note = random.choice(notes)
		text += " {}".format(note)	
		comment += " {}".format(note)
	if random.random() < 0.01:
		text = "zest of " + text
	if random.random() < 0.01:
		text = ing + " " + comment
		amount = ""
		mea = ""
		comment = ""
	if random.random() < 0.02:
		text = "salt"
		ing = "salt"
		amount = ""
		mea = ""
		comment = ""
	if random.random() < 0.01:
		text = "salt to taste"
		ing = "salt"
		amount = ""
		mea = ""
		comment = ""
	if ',' in text:
		text = '"'+text+'"'
	if ',' in item:
		item = '"'+item+'"'
	if ',' in comment:
		comment = '"'+comment+'"'
	return text, item, mea, amount, comment


print(randomIngredient())
with open("bootstrap.csv","w") as f:
	f.write("index,input,name,qty,range_end,unit,comment\n")
	for i in range(1000):
		text, item, measure, amount, comment = randomIngredient()
		f.write('{},{},{},{},,{},{}\n'.format(i,text,item,amount,measure,comment))

		
"""
python3 bootstrap.py
bin/generate_data --data-path=bootstrap.csv --count=10000 --offset=0 > tmp/train_file
crf_learn template_file tmp/train_file tmp/model_file 
"""
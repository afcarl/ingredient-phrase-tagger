#!/usr/bin/env python3
import sys
import os
import json
import tempfile
import subprocess

import re
import string


def tokenize(s):
    """
    Tokenize on parenthesis, punctuation, spaces and American units followed by a slash.

    We sometimes give American units and metric units for baking recipes. For example:
        * 2 tablespoons/30 mililiters milk or cream
        * 2 1/2 cups/300 grams all-purpose flour

    The recipe database only allows for one unit, and we want to use the American one.
    But we must split the text on "cups/" etc. in order to pick it up.
    """

    american_units = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'quart', 'pint']
    for unit in american_units:
        s = s.replace(unit + '/', unit + ' ')
        s = s.replace(unit + 's/', unit + 's ')

    tokens = []
    # for token in re.split(r'([,\(\)])?\s*', clumpFractions(s)):
    for token in re.split(r'([,\(\)])?\s', clumpFractions(s)):
        if token != '' and token != None:
            tokens.append(token)
    return tokens
    # return filter(None, re.split(r'([,\(\)])?\s*', clumpFractions(s)))

def joinLine(columns):
    return "\t".join(columns)

def clumpFractions(s):
    """
    Replaces the whitespace between the integer and fractional part of a quantity
    with a dollar sign, so it's interpreted as a single token. The rest of the
    string is left alone.

        clumpFractions("aaa 1 2/3 bbb")
        # => "aaa 1$2/3 bbb"
    """
    return re.sub(r'(\d+)\s+(\d)/(\d)', r'\1$\2/\3', s)

def cleanUnicodeFractions(s):
    """
    Replace unicode fractions with ascii representation, preceded by a
    space.

    "1\x215e" => "1 7/8"
    """

    fractions = {
        u'\x215b': '1/8',
        u'\x215c': '3/8',
        u'\x215d': '5/8',
        u'\x215e': '7/8',
        u'\x2159': '1/6',
        u'\x215a': '5/6',
        u'\x2155': '1/5',
        u'\x2156': '2/5',
        u'\x2157': '3/5',
        u'\x2158': '4/5',
        u'\xbc': ' 1/4',
        u'\xbe': '3/4',
        u'\x2153': '1/3',
        u'\x2154': '2/3',
        u'\xbd': '1/2',
        u'\xc2': '1/2',
        u'\u00be': '3/4',
        u'\u00bc': '1/4',
        u'\u00bd': '1/2',
        u'\u215b': '1/8',
    }

    for f_unicode, f_ascii in fractions.items():
        s = s.replace(f_unicode, ' ' + f_ascii)

    return s

def unclump(s):
    """
    Replacess $'s with spaces. The reverse of clumpFractions.
    """
    return re.sub(r'\$', " ", s)

def normalizeToken(s):
    """
    ToDo: FIX THIS. We used to use the pattern.en package to singularize words, but
    in the name of simple deployments, we took it out. We should fix this at some
    point.
    """
    return singularize(s)

def getFeatures(token, index, tokens):
    """
    Returns a list of features for a given token.
    """
    length = len(list(tokens))

    return [
        ("I%s" % index),
        ("L%s" % lengthGroup(length)),
        ("Yes" if isCapitalized(token) else "No") + "CAP",
        ("Yes" if insideParenthesis(token, tokens) else "No") + "PAREN"
    ]

def singularize(word):
    """
    A poor replacement for the pattern.en singularize function, but ok for now.
    """

    units = {
        "cups": u"cup",
        "tablespoons": u"tablespoon",
        "teaspoons": u"teaspoon",
        "pounds": u"pound",
        "ounces": u"ounce",
        "cloves": u"clove",
        "sprigs": u"sprig",
        "pinches": u"pinch",
        "bunches": u"bunch",
        "slices": u"slice",
        "grams": u"gram",
        "heads": u"head",
        "quarts": u"quart",
        "stalks": u"stalk",
        "pints": u"pint",
        "pieces": u"piece",
        "sticks": u"stick",
        "dashes": u"dash",
        "fillets": u"fillet",
        "cans": u"can",
        "ears": u"ear",
        "packages": u"package",
        "strips": u"strip",
        "bulbs": u"bulb",
        "bottles": u"bottle"
    }

    if word in units.keys():
        return units[word]
    else:
        return word

def isCapitalized(token):
    """
    Returns true if a given token starts with a capital letter.
    """
    return re.match(r'^[A-Z]', token) is not None

def lengthGroup(actualLength):
    """
    Buckets the length of the ingredient into 6 buckets.
    """
    for n in [4, 8, 12, 16, 20]:
        if actualLength < n:
            return str(n)

    return "X"

def insideParenthesis(token, tokens):
    """
    Returns true if the word is inside parenthesis in the phrase.
    """
    if token in ['(', ')']:
        return True
    else:
        line = " ".join(tokens)
        return re.match(r'.*\(.*'+re.escape(token)+'.*\).*',  line) is not None

def displayIngredient(ingredient):
    """
    Format a list of (tag, [tokens]) tuples as an HTML string for display.

        displayIngredient([("qty", ["1"]), ("name", ["cat", "pie"])])
        # => <span class='qty'>1</span> <span class='name'>cat pie</span>
    """

    return "".join([
        "<span class='%s'>%s</span>" % (tag, " ".join(tokens))
        for tag, tokens in ingredient
    ])

# HACK: fix this
def smartJoin(words):
    """
    Joins list of words with spaces, but is smart about not adding spaces
    before commas.
    """

    input = " ".join(words)

    # replace " , " with ", "
    input = input.replace(" , ", ", ")

    # replace " ( " with " ("
    input = input.replace("( ", "(")

    # replace " ) " with ") "
    input = input.replace(" )", ")")

    return input


def export_data(lines):
    """ Parse "raw" ingredient lines into CRF-ready output """
    output = []
    for line in lines:
        line_clean = re.sub('<[^<]+?>', '', line)
        line_clean = cleanUnicodeFractions(line_clean)
        tokens = tokenize(line_clean)

        for i, token in enumerate(tokens):
            features = getFeatures(token, i+1, tokens)
            output.append(joinLine([token] + features))
        output.append('')
    return '\n'.join(output)



def get_tagged_ingredients(ingredients,path_to_model_file):

    _, tmpFile = tempfile.mkstemp()
    with open(tmpFile, 'w') as outfile:
        outfile.write(export_data(ingredients))

    cmd = "crf_test -v 1 -m %s %s" % (path_to_model_file, tmpFile)
    output = subprocess.check_output(cmd.split()).decode('utf-8')
    os.system("rm %s" % tmpFile)

    ingredients = []
    ingredient = {}
    lastName = False
    output += "\n# 0"
    for line in output.split('\n'):
        if len(line) == 0:
            continue
        if line[0] == '#':
            if 'score' in ingredient:
                ingredients.append(ingredient)
            ingredient = {'score':0,'name':'','unit':'','qty':-1}
            ingredient['score'] = float(line.split()[1])
        if ingredient['name'] == '' and 'B-NAME' in line:
            ingredient['name'] = line.split()[0]
            lastName = True
        elif lastName and 'I-NAME' in line:
            ingredient['name'] += ' ' + line.split()[0]
            lastName = True 
        elif ingredient['unit'] == '' and 'B-UNIT' in line:
            ingredient['unit'] = singularize(line.split()[0])
            lastName = False
        elif ingredient['qty'] == -1 and 'B-QTY' in line:
            qty = line.split()[0]
            amount = 0
            for qt in qty.split('$'):
                try:
                    if '/' in qt:
                        amount += float(qt.split('/')[0]) / float(qt.split('/')[1])
                    else:
                        amount += float(qt)
                except:
                    pass
            ingredient['qty'] = amount
            lastName = False

    return ingredients


# ingredients = ["\u00be cup heavy cream","1 chicken breast","1 ¾ cups olive oil, refined"]
# path_to_model_file = 'tmp/model_file'
# print(json.dumps(get_tagged_ingredients(ingredients,path_to_model_file),indent=2))
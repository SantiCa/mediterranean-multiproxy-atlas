"""Source-label classification for coverage, never a proxy calibration.

Aliases only aid discovery. Native parameters, logarithms, taxonomic types,
fractions, units and counts are preserved unchanged in quantitative series.
"""
import re

ELEMENTS = {'aluminium':'Al', 'aluminum':'Al', 'titanium':'Ti', 'calcium':'Ca',
    'iron':'Fe', 'potassium':'K', 'silicon':'Si', 'zirconium':'Zr', 'rubidium':'Rb',
    'barium':'Ba', 'strontium':'Sr', 'manganese':'Mn', 'molybdenum':'Mo',
    'uranium':'U', 'thorium':'Th', 'vanadium':'V', 'rhenium':'Re', 'bromine':'Br',
    'chlorine':'Cl', 'magnesium':'Mg', 'sodium':'Na', 'sulfur':'S', 'sulphur':'S',
    'nickel':'Ni', 'copper':'Cu', 'zinc':'Zn'}
SYMBOLS = set(ELEMENTS.values())
TREES = r'Pinus|Quercus|Abies|Picea|Fagus|Alnus|Betula|Corylus|Carpinus|Ulmus|Fraxinus|Olea|Cedrus|Juniperus|Castanea|Juglans|Salix|Acer|Tilia|Pistacia|Ostrya|Taxus'


def ratio_alias(name):
    """Return Ti/Ca-style search alias while retaining log/ln and isotope labels."""
    text = name
    for word, symbol in ELEMENTS.items():
        text = re.sub(r'\b' + word + r'\b', symbol, text, flags=re.I)
    match = re.search(r'\b([A-Z][a-z]?)/([A-Z][a-z]?)\b', text)
    if not match or not all(x in SYMBOLS for x in match.groups()):
        return None
    prefix = 'ln ' if re.search(r'\bln[(-]', text) else 'log ' if re.search(r'\blog[(-]', text) else ''
    return prefix + '/'.join(match.groups())


def target_family(parameter, title='', realm='unknown'):
    """Assign a search family with explicit safeguards for misleading substrings."""
    if re.search(r'plant DNA|metabarcod|interstitial|pore.?water|dating|volcanic ash|speleothem|whole.rock|rock.eval', title, re.I):
        return None
    if re.search(r'\bpollen\b|\bpalynolog|\bbiomes\b', title, re.I):
        if re.match(r'^(?:' + TREES + r')(?:\b|\s)', parameter) or re.search(r'\bpollen\b|arboreal|semi.desert', parameter, re.I):
            return 'polen'
    if re.search(r'sortable silt|silt/clay|grain.size', title, re.I) and re.search(r'grain size|size fraction|silt/clay|clay/silt|sand|silt|clay', parameter, re.I):
        return 'corrientes'
    if re.search(r'Benthic Foraminifer Oxygen Index|Low oxygen indicators|Foraminifera, benthic.*(?:epi|infauna)|Oxygen, dissolved', parameter, re.I):
        return 'oxigenacion_bent'
    alias = ratio_alias(parameter)
    if alias and not re.search(r'foraminif|bulloides|ruber|pachyderma|Candona|ostracod', parameter, re.I):
        return 'xrf_razones'
    if realm == 'marine' and re.fullmatch(r'Molybdenum|Uranium|Vanadium|Rhenium|Manganese', parameter, re.I):
        return 'redox'
    return None

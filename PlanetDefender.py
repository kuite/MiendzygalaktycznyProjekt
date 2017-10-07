import openpyxl
import itertools
from ogame import OGame
from ogame.constants import Ships, Speed, Facilities, Buildings, Research, Defense, Missions


acc_doc = openpyxl.load_workbook('accounts.xlsx')
acc_sheet = acc_doc.active
cells = acc_sheet['A1': 'H1']

for a, b, c, d, e, f, g, h in cells:
    ogame = OGame(d.value, a.value, b.value, c.value)
    planets = ogame.get_planet_ids()
    while True:
        for planet_id in itertools.cycle(planets):
            name = ogame.get_planet_infos(planet_id)['planet_name']
            print('defending: ' + name)
            if 'matka' in name:
                defense = ogame.get_defense(planet_id)
                defend_rockets = defense['anti_ballistic_missiles']
                if defend_rockets < 70:
                    ogame.build(planet_id, (Defense['AntiBallisticMissiles'], 70))

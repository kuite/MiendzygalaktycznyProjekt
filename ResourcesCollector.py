from ogame import OGame
from ogame.constants import Ships, Speed, Facilities, Buildings, Research, Defense, Missions
import openpyxl
from tinydb import TinyDB, Query


class ResourcesCollector:
    def __init__(self, login, password, server, uni):
        self.ogame = OGame(uni, login, password, server)

    def collect_to(self, galaxy, system, planet):
        planets = self.ogame.get_planet_ids()
        for planet_id in planets:
            ships = [(Ships['SmallCargo'], 9999), (Ships['LargeCargo'], 9999)]
            speed = Speed['100%']
            where = {'galaxy': int(galaxy), 'system': int(system), 'position': int(planet)}
            mission = Missions['Transport']
            resources = {'metal': 999999999, 'crystal': 99999999, 'deuterium': 99999999}
            self.ogame.send_fleet(planet_id, ships, speed, where, mission, resources)
            print('collected from: {}'.format(self.ogame.get_planet_infos(planet_id)['planet_name']))


res_req_db = TinyDB('resources_requests.json')
requests = res_req_db.all()
requests = res_req_db.search(Query().first)
req_metal = requests['resources']


acc_doc = openpyxl.load_workbook('accounts.xlsx')
acc_sheet = acc_doc.active
cells = acc_sheet['A1': 'H1']
for a, b, c, d, e, f, g, h in cells:
    bot = ResourcesCollector(a.value, b.value, c.value, d.value)
    bot.collect_to(f.value, g.value, h.value)
    print('collected')
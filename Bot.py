from ogame import OGame
from ogame.constants import Ships, Speed, Facilities, Buildings, Research, Defense, Missions
import Utils
import openpyxl
from time import sleep
import random
from tinydb import TinyDB, Query
from datetime import datetime


class PlanetInfo:

    def __init__(self, planet_id, ogame):
        self.id = planet_id
        self.resources = ogame.get_resources(planet_id)
        self.resources_buildings = ogame.get_resources_buildings(planet_id)
        self.planet_overview = ogame.get_overview(planet_id)
        self.facilities = ogame.get_facilities(planet_id)
        self.level = self.resources_buildings['metal_mine'] + \
                     self.resources_buildings['crystal_mine'] + \
                     self.resources_buildings['solar_plant'] + \
                     self.resources_buildings['deuterium_synthesizer']
        self.infos = ogame.get_planet_infos(planet_id)   # TO DELETE
        self.ships = ogame.get_ships(planet_id)
        self.defense = ogame.get_defense(planet_id)


class Bot:
    def __init__(self, login, password, server, uni):
        self.login = login
        self.password = password
        self.server = server
        self.uni = uni
        self.ogame = OGame(self.uni, self.login, self.password, self.server)

        self.mother_id = self.ogame.get_planet_by_name('Planeta matka')
        self.planets = self.ogame.get_planet_ids()
        self.researches = self.ogame.get_research()
        self.weakest_planet_id = 0
        self.planet_infos = {}
        for planet_id in self.planets:
            print('Loading planet {}'.format(planet_id))
            self.planet_infos[planet_id] = PlanetInfo(planet_id, self.ogame)

        colony_doc = openpyxl.load_workbook('colony_planet_build.xlsx')
        colony_sheet = colony_doc.active
        self.colony_cells = colony_sheet['A1': 'C200']

        mother_doc = openpyxl.load_workbook('first_planet_build.xlsx')
        mother_sheet = mother_doc.active
        self.mother_cells = mother_sheet['A1': 'C250']

        shared_doc = openpyxl.load_workbook('shared_build.xlsx')
        shared_sheet = shared_doc.active
        self.shared_cells = shared_sheet['A1': 'C200']

        self.res_req_db = TinyDB('resources_requests.json')

    def start_def(self):
        for planet_info in self.planet_infos.values():
            planet_id = planet_info.id
            print('p Planet currently working: ' + planet_info.infos['planet_name'])
            start_time = datetime.now()
            self.check_minimum_large_cargos(planet_info)
            if planet_info.level > 95:
                if planet_id == self.mother_id:
                    self.send_expedition(planet_info)
                    self.check_defense_and_ships(planet_info)
                    self.send_resources_from_mother_if_possible(planet_info, self.res_req_db)
                else:
                    self.request_resources_for_next_build(planet_info, self.res_req_db, self.shared_cells)
                self.buildOnPlanetFromParsedXlsx(planet_id, self.shared_cells, planet_info)
                self.collect_resources(self.mother_id, planet_info)
            else:
                if planet_id == self.mother_id:
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.mother_cells, planet_info)
                else:
                    if planet_info.level < 1:
                        self.request_starter_resources(planet_info, self.res_req_db)
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.colony_cells, planet_info)

            time_elapsed = datetime.now() - start_time
            sleep_time = random.uniform(0.5, 1.3)
            print('p Planet handling time elapsed {}, random sleep time: {}[ms]'.format(time_elapsed, sleep_time))
            sleep(sleep_time)

    def start_eco(self):
        planets = self.planets
        researches = self.ogame.get_research()
        colony_slots = researches['astrophysics'] / 2

        if colony_slots > len(planets) - 1:
            self.colonize_planet_eco(self.planet_infos[self.mother_id])

        for planet_info in self.planet_infos.values():
            planet_id = planet_info.id
            print('Planet currently working: ' + planet_info.infos['planet_name'])
            self.check_defense_and_ships(planet_info)
            if planet_info.level > 90:
                if planet_id == self.mother_id:
                    self.send_expedition(planet_info)
                    self.check_defense_and_ships(planet_info)
                    self.send_resources_from_mother_if_possible(planet_info, self.res_req_db)
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.mother_cells, planet_info)
                else:
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.shared_cells, planet_info)
                    self.request_resources_for_next_build(planet_info, self.res_req_db, self.shared_cells)
                self.collect_resources(self.mother_id, planet_info)
            else:
                if planet_id == self.mother_id:
                    self.send_expedition(planet_info)
                    self.check_minimum_large_cargos(planet_info)
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.mother_cells, planet_info)
                else:
                    if planet_info.level < 1:
                        self.request_starter_resources(planet_info, self.res_req_db)
                    self.buildOnPlanetFromParsedXlsx(planet_id, self.colony_cells, planet_info)

            sleep_time = random.uniform(0.5, 1.4)
            sleep(sleep_time)
            print('p Planet {} handling finished, random sleep time: {}[ms]'.
                  format(planet_info.infos['planet_name'], sleep_time))

    @staticmethod
    def check_anti_ballistic_missiles_on_main_planet(ogame):
        # ogame = OGame(uni, login, password, server)
        mother_id = ogame.get_planet_by_name('Planeta matka')

        defense = ogame.get_defense(mother_id)
        defend_rockets = defense['anti_ballistic_missiles']
        if defend_rockets < 50:
            print('##### ALERT!! REBUILDING ROCKET DEFENSE: ' + defend_rockets)
            ogame.build(mother_id, (Defense['AntiBallisticMissiles'], 70))

    def colonize_planet_eco(self, planet_info):
        if planet_info.ships['colony_ship'] < 1:
            if len(planet_info.planet_overview['shipyard']) > 0:
                return
            self.ogame.build(self.mother_id, (Ships['ColonyShip'], 1))
            return
        mother_coordinates = planet_info.infos['coordinate']
        start_galaxy = mother_coordinates['galaxy']
        start_system = mother_coordinates['system']
        resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}
        slots = [11, 10, 9, 8, 7, 6, 5]
        current_system = start_system

        while True:
            for slot in slots:
                destination = {'galaxy': start_galaxy, 'system': current_system, 'position': slot}
                self.ogame.send_fleet(self.mother_id, [(Ships['ColonyShip'], 1)], Speed['100%'],
                                      destination, Missions['Colonize'], resources)

                if self.ogame.get_ships(self.mother_id)['colony_ship'] < 1:
                    print('skolonizowano: ' + str(destination))
                    return

            system_step = start_system - current_system
            if system_step == 0:
                current_system += 1
            elif system_step < 0:
                current_system = start_system + system_step
            elif system_step > 0:
                current_system = start_system + system_step + 1

            if system_step > 50:
                return

    def check_minimum_large_cargos(self, planet_info):
        if len(planet_info.planet_overview['shipyard']) > 0:
            return
        ships = planet_info.ships
        dt_count = 0

        if planet_info.level > 70:
            dt_count = 5
        if planet_info.level > 80:
            dt_count = 15

        dt = int(ships['large_cargo'])
        if dt < dt_count:
            self.ogame.build(planet_info.id, (Ships['LargeCargo'], dt_count - dt))

    def check_defense_and_ships(self, planet_info):
        if len(planet_info.planet_overview['shipyard']) > 0:
            return

        defense = planet_info.defense
        ships = planet_info.ships
        resources_buildings = planet_info.resources_buildings
        facilities = planet_info.facilities
        planet_id = planet_info.id

        silos_level = int(facilities['missile_silo'])

        ldl = int(defense['light_laser'])
        gauses = int(defense['gauss_cannon'])
        anti_rockets = int(defense['anti_ballistic_missiles'])
        solars = int(ships['solar_satellite'])
        probes = int(ships['espionage_probe'])
        dt = int(ships['large_cargo'])
        metal_mine = int(resources_buildings['metal_mine'])
        crystal_mine = int(resources_buildings['crystal_mine'])
        shipyard = int(facilities['shipyard'])

        ldl_count = 0
        anti_rockets_count = 0
        gauss_count = 0
        solars_count = 0
        probes_count = 0
        dt_count = 0

        if planet_info.level > 75:
            dt_count = 5 - dt
            probes_count = 1 - probes

        if crystal_mine > 15:
            ldl_count = 113 - ldl
            probes_count = 1 - probes
        if shipyard >= 8 and crystal_mine >= 19:
            ldl_count = 200 - ldl
        if shipyard >= 8 and crystal_mine > 23 and int(facilities['missile_silo']) >= 2:
            ldl_count = 500 - ldl
            anti_rockets_count = 20 - anti_rockets
            gauss_count = 20 - gauses
            solars_count = 50 - solars
            dt_count = 25 - dt
        if silos_level >= 2:
            anti_rockets_count = silos_level * 10

        if anti_rockets_count > 0:
            self.ogame.build(planet_id, (Defense['AntiBallisticMissiles'], anti_rockets_count))
        if gauss_count > 0:
            self.ogame.build(planet_id, (Defense['GaussCannon'], gauss_count))
        if ldl_count > 0:
            self.ogame.build(planet_id, (Defense['LightLaser'], ldl_count))
        if solars_count > 0:
            self.ogame.build(planet_id, (Ships['SolarSatellite'], solars_count))
        if probes_count > 0:
            self.ogame.build(planet_id, (Ships['EspionageProbe'], probes_count))
        if dt_count > 0:
            self.ogame.build(planet_id, (Ships['LargeCargo'], dt_count))

    def buildOnPlanetFromParsedXlsx(self, planet_id, cells, planetInfo):
        researches = self.researches
        ships = self.planet_infos[planet_id].ships
        defense = self.planet_infos[planet_id].defense
        print('DEBUG: c1, c2, c3 in cells:')
        for c1, c2, c3 in cells:
            if c1.value == '':
                return
            if c1.value in defense and defense[c1.value] < c2.value:
                if len(self.ogame.get_overview(planet_id)['shipyard']) > 0:
                    continue
                defense_objects_count = int(c2.value) - int(defense[c1.value])
                print('DEBUG: building defense: ' + c1.value + " in number of: " + str(defense_objects_count))
                self.ogame.build(planet_id, (Defense[c3.value], defense_objects_count))
                return
            elif c1.value in ships and ships[c1.value] < c2.value:
                if len(planetInfo.planet_overview['shipyard']) > 0:
                    continue
                ships_count = int(c2.value) - int(ships[c1.value])
                if ships_count < 0:
                    continue
                print('DEBUG: building ship: ' + c1.value + " in number of: " + str(ships_count))
                self.ogame.build(planet_id, (Ships[c3.value], ships_count))
                return
            elif c1.value in planetInfo.resources_buildings and planetInfo.resources_buildings[c1.value] < c2.value:
                if len(planetInfo.planet_overview['buildings']) > 0:
                    continue
                print('DEBUG: building build: ' + c1.value + ' on level: ' + str(c2.value))
                self.ogame.build(planet_id, Buildings[c3.value])
                return
            elif c1.value in planetInfo.facilities and planetInfo.facilities[c1.value] < c2.value:
                if len(planetInfo.planet_overview['buildings']) > 0:
                    continue
                print('DEBUG: building facilities: ' + c1.value + ' on level: ' + str(c2.value))
                self.ogame.build(planet_id, Facilities[c3.value])
                return
            elif c1.value in researches and researches[c1.value] < c2.value:
                if len(planetInfo.planet_overview['research']) > 0:
                    continue
                print('DEBUG: building technology: ' + c1.value + ' on level: ' + str(c2.value))
                self.ogame.build(planet_id, Research[c3.value])
                return

    def send_resources_from_mother_if_possible(self, mother_info, res_req_db):
        print('sending resources if possible from: '.format(mother_info.infos['planet_name']))
        # check if there is pending request in database
        # send all resources if have for whole request ONLY
        requests = res_req_db.all()
        # requests = None
        if requests is None:
            return
        lowest_request = 99999999999
        working_request = None
        for request in requests:
            if request['requesting']['galaxy'] != mother_info.infos['coordinate']['galaxy'] or \
                    self.login != request['login'] or self.uni != request['uni']:
                continue

            req_metal = request['metal']
            req_crystal = request['crystal']
            req_deuterium = request['deuterium']
            req_total_cost = req_metal + 2*req_crystal + 2.1*req_deuterium

            # find lowest request
            if req_total_cost < lowest_request:
                working_request = request
                break

        if working_request is None:
            return

        req_metal = working_request['metal']
        req_crystal = working_request ['crystal']
        req_deuterium = working_request['deuterium']
        req_building = working_request['building']
        req_level = working_request['level']


        # check if building is more advanced than on mother if yes return someday
        metal = mother_info.resources['metal']
        crystal = mother_info.resources['crystal']
        deuterium = mother_info.resources['deuterium']
        total_resources = metal + crystal + deuterium

        if metal > req_metal and crystal > req_crystal and deuterium > req_deuterium:
            dt_count = int(total_resources / 25000) + 1
            ships = [(Ships['LargeCargo'], dt_count)]
            speed = Speed['100%']
            where = {'galaxy': working_request['requesting']['galaxy'],
                     'system': working_request['requesting']['system'],
                     'position': working_request['requesting']['position']}
            mission = Missions['Transport']
            request_resources = {'metal': req_metal, 'crystal': req_crystal, 'deuterium': req_deuterium}
            self.ogame.send_fleet(mother_info.id, ships, speed, where, mission, request_resources)
            print('-> sending resources from mother to: ' + str(where))

    def collect_resources(self, mother_id, planet_info):
        dt = planet_info.ships['large_cargo']
        capacity = dt * 25000
        resources = planet_info.resources['metal'] + \
                    planet_info.resources['crystal'] + \
                    planet_info.resources['deuterium']
        if resources > capacity * 0.75 and dt > 5:
            ships = [(Ships['LargeCargo'], 9999)]
            speed = Speed['100%']
            where = self.planet_infos[mother_id].infos['coordinate']
            mission = Missions['Transport']
            resources = {'metal': 999999999, 'crystal': 99999999, 'deuterium': 99999999}
            self.ogame.send_fleet(planet_info.id, ships, speed, where, mission, resources)
            print('collect_resources from: ' + planet_info.infos['planet_name'] + ' to mother planet')

    def request_starter_resources(self, planet_info, res_req_db):
        exst_req = res_req_db.search(Query().requesting == planet_info.infos['coordinate'])
        if len(exst_req) > 0:
            return

        res_req_db.insert({'requesting': planet_info.infos['coordinate'], 'metal': 50000, 'crystal': 50000,
                           'deuterium': 20000})

    def send_expedition(self, planet_info):
        mother_coordinates = planet_info.infos['coordinate']
        galaxy = mother_coordinates['galaxy']
        system = mother_coordinates['system']
        system_delta = random.randint(-5, 5)
        dt_count = 0

        if planet_info.level > 70:
            dt_count = 5
        if planet_info.level > 80:
            dt_count = 15
        if planet_info.level > 95:
            dt_count = 100
        if planet_info.level > 100:
            dt_count = 250

        ships = [(Ships['EspionageProbe'], 1), (Ships['LargeCargo'], dt_count)]
        speed = Speed['100%']
        where = {'galaxy': galaxy, 'system': system + system_delta, 'position': 16}
        mission = Missions['Expedition']
        resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}
        self.ogame.send_fleet(planet_info.id, ships, speed, where, mission, resources)
        print('send expedition from mother to: {}'.format(where))

    def request_resources_for_next_build(self, planet_info, res_req_db, shared_cells):
        print('DEBUG: exst_req = res_req_db.search(Query().requesting == planet_info.infos[coordinate])')
        exst_req = res_req_db.search(Query().requesting == planet_info.infos['coordinate'])
        # if exst_req is None:
        #     return
        print('DEBUG: len(exst_req)')
        if len(exst_req) > 0:
            return
        print('DEBUG: for c1, c2, c3 in shared_cells:')
        for c1, c2, c3 in shared_cells:
            if c1.value == '' or c1.value == 'solar_satellite':
                continue
            cost = Utils.calc_build_cost(c1.value, c2.value)
            res_req_db.insert({'requesting': planet_info.infos['coordinate'], 'metal': cost[0], 'crystal': cost[1],
                               'deuterium': cost[2], 'building': c1.value, 'level': c2.value, 'login': self.login,
                               'uni': self.uni})

            # elif c1.value in planet_info.resources_buildings and planet_info.resources_buildings[c1.value] < c2.value:
            #     cost = Utils.calc_build_cost(c1.value, c2.value)
            #    res_req_db.insert({'requesting': planet_info.infos['coordinate'], 'metal': cost[0], 'crystal': cost[1],
            #                       'deuterium': cost[2], 'building': c1.value, 'level': c2.value, 'login': self.login})
            #     return
            # elif c1.value in planet_info.facilities and planet_info.facilities[c1.value] < c2.value:
            #     cost = Utils.calc_build_cost(c1.value, c2.value)
            #     res_req_db.insert({'requesting': planet_info.infos['coordinate'], 'metal': cost[0], 'crystal': cost[1],
            #                        'deuterium': cost[2], 'building': c1.value, 'level': c2.value})
            #     return

    def build_next_build(self, planet_info, shared_cells):
        pass

    def check_anti_ballistic_missiles(self):
        for planet_id in self.planet_infos:
            name = self.ogame.get_planet_infos(planet_id)['planet_name']
            if 'matka' in name:
                # print('defending: ' + name)
                defense = self.ogame.get_defense(planet_id)
                defend_rockets = defense['anti_ballistic_missiles']
                if defend_rockets < 50:
                    self.ogame.build(planet_id, (Defense['AntiBallisticMissiles'], 70))

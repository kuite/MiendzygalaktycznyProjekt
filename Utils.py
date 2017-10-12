import math

techData = \
    {
        'metal_mine': [60, 15, 0, 1.5],
        'crystal_mine': [48, 24, 0, 1.6],
        'deuterium_synthesizer': [225, 75, 0, 1.5],
        'solar_plant': [75, 30, 0, 1.5],
        'robotics_factory': [400, 120, 200, 2],
        'nanite_factory': [1000000, 500000, 100000, 2],
        'shipyard': [400, 200, 100, 2],
        'terraformer': [0, 50000, 100000, 2],
        'astrophysics': [4000, 8000, 4000, 1.75],
        'plasma_technology': [2000, 4000, 1000, 2],
        'msbn': [240000, 400000, 160000, 2],
        'weapons_technology': [800, 200, 0, 2],
        'shielding_technology': [200, 600, 0, 2],
        'metal_storage': [1000, 0, 0, 2],
        'crystal_storage': [1000, 50, 0, 2],
        'deuterium_tank': [1000, 1000, 0, 2],
        'fusion_reactor': [900, 360, 180, 1.8]
    }


def calc_build_cost(tech_name, tech_level):
    if tech_level < 1:
        return [0, 0, 0]
    data = techData[tech_name]
    if data is None:
        return [0, 0, 0]
    cost = [0, 0, 0]

    for i in range(3):
        cost[i] = math.floor(data[i] * math.pow(data[3], (tech_level - 1)))

    return cost


def get_next_build(planet_info):
    building = ['metal_mine', 1]
    metal_lvl = planet_info.resources_buildings['metal_mine']
    crystal_lvl = planet_info.resources_buildings['crystal_mine']
    solar_lvl = planet_info.resources_buildings['solar_plant']
    deuter_lvl = planet_info.resources_buildings['deuterium_synthesizer']



    return building

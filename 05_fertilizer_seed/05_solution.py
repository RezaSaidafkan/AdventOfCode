from typing import Dict, List, Tuple
from pydantic import BaseModel
from rich import print


class Line(BaseModel):
    destination_range_start: int
    source_range_start: int
    range_length: int

RawMaps = Dict[str, List[Line]]

Seeds = List[int]

Map = dict[int, int]

        
def _get_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def _parser(input: str) -> Tuple[Seeds, RawMaps]:
    lines = input.split('\n')
    seeds = list(map(int, lines[0].split()[1:]))
    
    raw_maps: RawMaps = {
        'seed_to_soil': {},
        'soil_to_fertilizer': {},
        'fertiziler_to_water': {},
        'water_to_light': {},
        'light_to_temperature': {},
        'temperature_to_humidity': {},
        'humidity_to_location': {}
    }
    
    current_map = None
    for line in lines[1:]:
        if line.startswith('seed-to-soil map'):
            current_map = 'seed_to_soil'
        elif line.startswith('soil-to-fertilizer map:'):
            current_map = 'soil_to_fertilizer'
        elif line.startswith('fertilizer-to-water map:'):
            current_map = 'fertiziler_to_water'
        elif line.startswith('water-to-light map:'):
            current_map = 'water_to_light'
        elif line.startswith('light-to-temperature map:'):
            current_map = 'light_to_temperature'
        elif line.startswith('temperature-to-humidity map:'):
            current_map = 'temperature_to_humidity'
        elif line.startswith('humidity-to-location map:'):
            current_map = 'humidity_to_location'
        elif current_map and line.strip():
            parts = line.split()
            line = Line(
                destination_range_start=int(parts[0]),
                source_range_start=int(parts[1]),
                range_length=int(parts[2])
            )
            lines_list = raw_maps.get(current_map, [])
            if lines_list:
                lines_list.append(line)
            else:
                lines_list = [line]
            raw_maps[current_map] = lines_list
                
    return seeds, raw_maps

def _convert_line_to_map_table(line: Line) -> Map:
    source_range = range(line.source_range_start, line.source_range_start + line.range_length)
    destination_range = range(line.destination_range_start, line.destination_range_start + line.range_length)
    return dict(zip(source_range, destination_range))

def get_range_map_table(lines: List[Line]) -> Map:
    mapping = {}
    for line in lines:
        line_map = _convert_line_to_map_table(line)
        mapping.update(line_map)
    
    return mapping

def map_table_function(raw_map: List[Line], input: int) -> int:
    ranged_map = get_range_map_table(raw_map)
    print(ranged_map)
    return ranged_map.get(input, input)

def dynamic_function(raw_map: List[Line], input: int) -> int:
    for line in raw_map:
        if line.source_range_start <= input < line.source_range_start + line.range_length:
            return line.destination_range_start + (input - line.source_range_start)
    return input

def find_lowest_location(seeds, raw_maps):
    # Parse the input file to get the mappings
    
    location_numbers = []
    
    conversion_function = dynamic_function
    
    for seed in seeds:
        print(f"Seed: {seed}")
        soil = conversion_function(raw_maps["seed_to_soil"], seed)
        fertilizer = conversion_function(raw_maps["soil_to_fertilizer"], soil)
        water = conversion_function(raw_maps["fertiziler_to_water"], fertilizer)
        light = conversion_function(raw_maps["water_to_light"], water)
        temperature = conversion_function(raw_maps["light_to_temperature"], light)
        humidity = conversion_function(raw_maps["temperature_to_humidity"], temperature)
        location = conversion_function(raw_maps["humidity_to_location"], humidity)
        location_numbers.append(location)
    
    lowest_location = min(location_numbers)
    
    print(f"The lowest location number is {lowest_location}")


file_path = "/Users/RSAIDAFK/rise/repos/aoc/05_fertilizer_seed/input.txt"
file = _get_file(file_path)
# print(file)
seeds, raw_maps = _parser(file)
# import pprint
# pprint.pprint(_parser(file), indent=4, width=1)
# print(_parser(file))
# import json
# print(json.dumps(_parser(file), indent=4))
find_lowest_location(seeds, raw_maps)
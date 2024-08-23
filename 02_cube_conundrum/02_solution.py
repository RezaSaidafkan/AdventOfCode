from pathlib import Path

def get_input(file_name):
    with open(Path(__file__).parent / file_name) as file:
        return [line.strip() for line in file.readlines()]

def parse_game(data):
    data = data.replace(", ", ",").replace(": ", ":").replace("; ", ";")
    game_id, data = data.split(":")
    game_id = int(game_id[5:])
    game_sets = data.split(";")
    return game_id, game_sets
 
def parse_ball(set_data):
    parsed_set = {"red": 0,
                  "blue": 0,
                  "green": 0}
    for ball in set_data.split(","):
        ball_count, ball_color = ball.split(" ")
        parsed_set[ball_color] = int(ball_count)
    return parsed_set

def run_game(game_input, limits):
    data = get_input(game_input)
    counter = 0
    for game_round in data:
        game_id, game_sets = parse_game(game_round)
        parsed_game_sets = [parse_ball(game_set) for game_set in game_sets]
        if all([logic(parsed_game_set, limits) for parsed_game_set in parsed_game_sets]):
            print(f"Game won, {game_id}")
            counter += game_id
    return counter

def logic(game_result, limits):
    return all([game_result["red"] <= limits["red"], game_result["green"] <= limits["green"], game_result["blue"] <= limits["blue"]])

if __name__ == "__main__":
    limits = {"red": 12, "green": 13, "blue": 14}
    expected_output = 1867
    output = run_game("input1.txt", limits)
    print("resulted_output: ", output)
    assert output == expected_output
from pathlib import Path


def _is_int(value):
    try:
        int_value = int(value)
        return int_value
    except ValueError:
        return False


def get_calibration_value(line):
    first_int = None
    last_int = None
    for l in line:
        if first_int:= _is_int(l):
            break
    for i in range(len(line)-1, -1, -1):
        l = line[i]
        if last_int:= _is_int(l):
            break
    return int(f"{first_int}{last_int}")
    
def get_combined_calibration_value(input):
    lines = input.split("\n")
    return sum([get_calibration_value(line) for line in lines])

def _read_input_file(input_path):
    with open(input_path, "r") as file:
        return file.read()


input_path = Path(input("Enter the path to the input file: "))


result = get_combined_calibration_value(_read_input_file(input_path))
expected_result = 55108


if result == expected_result:
    print(f"Test passed, the expected result is '{expected_result}'")
    
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
        if new_int:= _is_int(l):
            if not first_int:
                first_int = new_int
                last_int = new_int
            else:
                last_int = new_int
    return int(f"{first_int}{last_int}")
    
def get_combined_calibration_value(input):
    return sum([get_calibration_value(line) for line in input])

def _read_input_file(input_path):
    with open(input_path, "r") as file:
        return file.read().splitlines()


input_path = Path(input("Enter the path to the input file: "))


result = get_combined_calibration_value(_read_input_file(input_path))
print(result)
expected_result = 53974


if result == expected_result:
    print(f"Test passed, the expected result is '{expected_result}'")
    
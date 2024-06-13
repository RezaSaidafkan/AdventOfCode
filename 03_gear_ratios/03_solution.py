from pathlib import Path
from typing import Tuple
import functools

def _open_matrix(file_name):
    with open(Path(__file__).parent / file_name) as file:
        return [line.strip() for line in file.readlines()]

def print_matrix(matrix):
    for row in matrix:
        print(row)


def _parse_row_token(row, j):
    token, tokens = [], []
    on_a_token = False
    for i, element in enumerate(row):
        if not on_a_token:
            token = []
        if element.isnumeric():
            token.append((j, i, int(element)))
            on_a_token = True
        else:
            on_a_token = False
            if token:
                tokens.extend([token])
    return tokens


def _find_all_tokens(matrix):
    all_tokens = []
    for j, row in enumerate(matrix):
        all_tokens.extend(_parse_row_token(row, j))        
    return all_tokens

def _create_left_pad_element(element, matrix):
    i, j = element[0], element[1]
    return (i, j-1, matrix[i][j-1])

def _create_right_pad_element(element, matrix):
    i, j = element[0], element[1]
    return (i, j+1, matrix[i][j+1])

def _scan_token(token, matrix):
    output_result = []
    new_token = token.copy()
    left_most_token = new_token.pop(0)
    right_most_token = new_token.pop(-1)
    middle_elements = new_token
    
    left_output_result = _check_left(left_most_token, matrix)
    right_output_result = _check_right(right_most_token, matrix)
    
    check_span = []
    if left_output_result[1]:
        left_pad_element = _create_left_pad_element(left_most_token, matrix)
        check_span.append(left_pad_element)
        
    check_span.extend([left_most_token, *middle_elements, right_most_token])
    
    if right_output_result[1]:
        right_pad_element = _create_right_pad_element(right_most_token, matrix)
        check_span.append(right_pad_element)

    up_down_outout_result = []
    for element in check_span:
        up_down_outout_result.append(_check_up(element, matrix))
        up_down_outout_result.append(_check_down(element, matrix))
    
    output_result.insert(0, left_output_result)
    output_result.extend(up_down_outout_result)
    output_result.insert(-1, right_output_result)
    print("token: ", token, " ".join([f"{o_r[0]}: {o_r[1]}\t" for o_r in output_result]))
    
    return output_result

def _check_left(token, matrix) -> Tuple[str, str, bool]:
    i, j = token[0], token[1]
    if j == 0:
        return "'left edge'", None, False
    else:
        left_element = matrix[i][j-1]
        return f"'left'", left_element, _check_token(i, j-1, matrix)

def _check_right(token, matrix) -> Tuple[str, str, bool]:
    i, j = token[0], token[1]
    if j == len(matrix[0]) - 1:
        return "'right edge'", None, False
    else:
        right_element = matrix[i][j+1]
        return f"'right'", right_element, _check_token(i, j+1, matrix)

def _check_up(element, matrix) -> Tuple[str, str, bool]:
    i, j = element[0], element[1]
    if i == 0:
        return "'upper edge'", None, False
    else:
        upper_element = matrix[i-1][j]
        return f"'up'", upper_element, _check_token(i-1, j, matrix)

def _check_down(token, matrix) -> Tuple[str, str, bool]:
    i, j = token[0], token[1]
    if i == len(matrix) - 1:
        return "'lower edge'", None, False
    else:
        lower_element = matrix[i+1][j]
        return f"'down'", lower_element, _check_token(i+1, j, matrix)


def _check_token(i, j, matrix):
    return matrix[i][j] == "."

def check_token(token, output_result):
    if any([not o_r[2] for o_r in output_result]):
        return int("".join([str(element[2]) for element in token]))
    

if __name__ == "__main__":
    matrix = _open_matrix("Example3.txt")
    all_tokens = _find_all_tokens(matrix)
    print_matrix(matrix)
    output_result = []
    for token in all_tokens:
        checked_elements = _scan_token(token, matrix)
        if true_token := check_token(token, checked_elements):
            output_result.append(true_token)
        
        
    print("output_result: ", sum(output_result))
    
    
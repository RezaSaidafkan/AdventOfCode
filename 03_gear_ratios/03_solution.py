from pathlib import Path
from typing import Tuple, List
from dataclasses import dataclass
from enum import Enum
from logging import getLogger, basicConfig, INFO, DEBUG

logger = getLogger(__name__)


class CheckType(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

class Reason(Enum):
    EDGE = "edge"
    VALUE = "value"
    
@dataclass
class CheckResult:
    reason: Reason
    value: str
    verdict: bool
    type: CheckType
    
    def __repr__(self) -> str:
        return f"{self.type}: '{self.value}'"

@dataclass
class Token:
    element: Tuple[int, int]
    value: int
    checks: List[CheckResult]
    
    def __repr__(self) -> str:
        # return f"{self.value}\t" + " \t".join([f"{check.type}: {check.value}" for check in self.checks if check.verdict])
        return f"{self.value}\t"

@dataclass
class Partnumber:
    tokens: List[Token]
    
    def __repr__(self) -> str:
        # return "\n".join([repr(token) for token in self.tokens])
        return str(self.value())
    
    def value(self) -> int:
        return int("".join([str(token.value) for token in self.tokens]))


def _open_matrix(file_name):
    with open(Path(__file__).parent / file_name) as file:
        return [line.strip() for line in file.readlines()]

def print_matrix(matrix):
    for row in matrix:
        print(row)

def _parse_row_partnumbers(row: str, i: int) -> List[Partnumber]:
    partnumber: Partnumber
    partnumbers: List[Partnumber] = []
    
    on_a_token = False
    for j, element in enumerate(row):
        if not on_a_token:
            partnumber = Partnumber(tokens=[])
        if element.isnumeric():
            partnumber.tokens.append(Token(element=(i, j), value=int(element), checks=[]))
            on_a_token = True
        else:
            on_a_token = False
            if partnumber.tokens:
                partnumbers.append(partnumber)
    return partnumbers


def _find_matrix_partnumbers(matrix: List[List[str]]) -> List[Partnumber]:
    matrix_partnumbers = []
    for i, row in enumerate(matrix):
        matrix_partnumbers.extend(_parse_row_partnumbers(row, i))
    return matrix_partnumbers

def _create_left_pad_token(element, matrix):
    i, j = element[0], element[1]
    return Token(element=(i, j-1), value=matrix[i][j-1], checks=[])

def _create_right_pad_token(element, matrix):
    i, j = element[0], element[1]
    return Token(element=(i, j+1), value=matrix[i][j+1], checks=[])

def _scan_partnumber(partnumber: Partnumber, matrix: List[List[str]]) -> Partnumber:
    logger.debug(f"partnumber: {partnumber}")
    if partnumber.value() == 658:
        # pdb.set_trace()
        pass
    new_tokens = partnumber.tokens.copy()
    left_most_token = new_tokens.pop(0)
    _check_left_token(left_most_token, matrix)
    
    right_most_token: Token = None
    if new_tokens:
        right_most_token = new_tokens.pop(-1)
    else:
        right_most_token = left_most_token
    _check_right_token(right_most_token, matrix)
        
    middle_tokens = new_tokens
    
    check_span_tokens: List[Token] = []
    if not left_most_token.checks[0].verdict:
        left_pad_element = _create_left_pad_token(left_most_token.element, matrix)
        check_span_tokens.append(left_pad_element)
        
    check_span_tokens.extend([left_most_token, *middle_tokens])
    if right_most_token:
        check_span_tokens.append(right_most_token)
        
    if not right_most_token.checks[0].verdict:
        right_pad_element = _create_right_pad_token(right_most_token.element, matrix)
        check_span_tokens.append(right_pad_element)
    
    for token in check_span_tokens:
        _check_up_token(token, matrix)
        _check_down_token(token, matrix)
        
    logger.debug("check_span_tokens:")
    logger.debug('\n'.join([repr(token) for token in check_span_tokens]))
    
    if _evaluate_partnumber(check_span_tokens):
        return partnumber
    

def _check_left_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if j == 0:
        token.checks.append(CheckResult(reason=Reason.EDGE, value=None, verdict=False, type=CheckType.LEFT))
    else:
        left_element = (i, j-1)
        value = matrix[i][j-1]
        result = _check_element(left_element, matrix)
        if not result:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=False, type=CheckType.LEFT))
        else:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=True, type=CheckType.LEFT))


def _check_right_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if j == len(matrix[0]) - 1:
        token.checks.append(CheckResult(reason=Reason.EDGE, value=None, verdict=False, type=CheckType.RIGHT))
    else:
        right_element = (i, j+1)
        value = matrix[i][j+1]
        result = _check_element(right_element, matrix)
        if not result:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=False, type=CheckType.RIGHT))
        else:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=True, type=CheckType.RIGHT))

def _check_up_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if i == 0:
        token.checks.append(CheckResult(reason=Reason.EDGE, value=None, verdict=False, type=CheckType.UP))
    else:
        upper_element = (i-1, j)
        value = matrix[i-1][j]
        result = _check_element(upper_element, matrix)
        if not result:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=False, type=CheckType.UP))
        else:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=True, type=CheckType.UP))
    
def _check_down_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if i == len(matrix) - 1:
        token.checks.append(CheckResult(reason=Reason.EDGE, value=None, verdict=False, type=CheckType.DOWN))
    else:
        lower_element = (i+1, j)
        value = matrix[i+1][j]
        result = _check_element(lower_element, matrix)
        if not result:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=False, type=CheckType.DOWN))
        else:
            token.checks.append(CheckResult(reason=Reason.VALUE, value=value, verdict=True, type=CheckType.DOWN))

def _check_element(element, matrix):
    i, j = element[0], element[1]
    value = matrix[i][j]
    if value == ".":
        return False
    return value

def _evaluate_partnumber(check_span_tokens: List[Token]):
    return [token for token in check_span_tokens if any([check.verdict for check in token.checks])]
    

if __name__ == "__main__":
    import pdb
    basicConfig(level=INFO)
    matrix = _open_matrix("input.txt")
    #print_matrix(matrix)
    all_partnumbers = _find_matrix_partnumbers(matrix)
    all_checked_partnumbers = []
    for partnumber in all_partnumbers:
        if checked_partnumber := _scan_partnumber(partnumber, matrix):
            logger.debug(f"checked_partnumber {checked_partnumber}")
            all_checked_partnumbers.append(checked_partnumber.value())
    # logger.info(f"output_result:\n{all_checked_partnumbers}\n{sum(all_checked_partnumbers)}")
    print(all_checked_partnumbers, sum(all_checked_partnumbers))
    
    
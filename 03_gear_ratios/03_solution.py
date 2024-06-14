from pathlib import Path
from typing import Tuple, List
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
import re

logger = getLogger(__name__)


class TokenType(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    NORMAL = "normal"
    

@dataclass
class CheckResult:
    token_type: TokenType
    value: str
    verdict: bool
    
    def __repr__(self) -> str:
        return f"{self.token_type} '{self.value}'"

@dataclass
class Token:
    element: Tuple[int, int]
    value: int
    checks: List[CheckResult]
    
    def __repr__(self) -> str:
        if VERBOSE:
            if checks := [f"{check}" for check in self.checks]:
                return f"[{self.value} - {' '.join(checks)}]"
        return f"{self.value}"

@dataclass
class Partnumber:
    tokens: List[Token]
    
    def __repr__(self) -> str:
        if VERBOSE:
            return "".join([repr(token) for token in self.tokens]) + "\t" + str(self.tokens[0].element) + "\t" + str(self)
        return "".join([repr(token) for token in self.tokens])
        
    def value(self) -> int:
        return int("".join([str(token.value) for token in self.tokens]))
    
    def __str__(self) -> str:
        return str(self.value())


def _open_matrix(file_name):
    with open(Path(__file__).parent / file_name) as file:
        return [line.strip() for line in file.readlines()]

def _find_matrix_partnumbers(matrix: List[List[str]]) -> List[Partnumber]:
    return [Partnumber(tokens=
                       [Token(element=(i,j), value=matrix[i][j], checks=[]) for j in range(partnumbers.start(), partnumbers.end())]
                       ) 
            for i, row in enumerate(matrix) for partnumbers in re.finditer(r'\d+', row)]
    
def _create_left_pad_token(element, matrix):
    i, j = element[0], element[1]
    return Token(element=(i, j-1), value=matrix[i][j-1], checks=[])

def _create_right_pad_token(element, matrix):
    i, j = element[0], element[1]
    return Token(element=(i, j+1), value=matrix[i][j+1], checks=[])

def _scan_partnumber(partnumber: Partnumber, matrix: List[List[str]]) -> Partnumber:
    slice_partnumber = partnumber.tokens.copy()
    
    left_most_token = slice_partnumber.pop(0)
    _check_left_token(left_most_token, matrix)
    
    # check if the new partnumber has any 'right' tokens left
    right_most_token: Token = None
    if slice_partnumber:
        right_most_token = slice_partnumber.pop(-1)
    else:
        right_most_token = left_most_token
    _check_right_token(right_most_token, matrix)
        
    middle_tokens = slice_partnumber
    
    check_span_tokens: List[Token] = []
    
    check_span_tokens.extend([left_most_token, *middle_tokens])
    if left_most_token.checks[0].token_type == TokenType.NORMAL:
        left_pad_element = _create_left_pad_token(left_most_token.element, matrix)
        check_span_tokens.insert(0, left_pad_element)
        
    if right_most_token:
        check_span_tokens.append(right_most_token)
        
    if right_most_token.checks[0].token_type == TokenType.NORMAL:
        right_pad_element = _create_right_pad_token(right_most_token.element, matrix)
        check_span_tokens.append(right_pad_element)
    
    for token in check_span_tokens:
        _check_up_token(token, matrix)
        _check_down_token(token, matrix)
        
    if _evaluate_partnumber(check_span_tokens):
        return partnumber
    

def _check_left_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if j == 0:
        token.checks.append(CheckResult(token_type=TokenType.LEFT, value=None, verdict=False))
    else:
        left_element = (i, j-1)
        value = matrix[i][j-1]
        result = _check_element(left_element, matrix)
        if not result:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=False))
        else:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=True))

def _check_right_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if j == len(matrix[0]) - 1:
        token.checks.append(CheckResult(token_type=TokenType.RIGHT, value=None, verdict=False))
    else:
        right_element = (i, j+1)
        value = matrix[i][j+1]
        result = _check_element(right_element, matrix)
        if not result:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=False))
        else:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=True))

def _check_up_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if i == 0:
        token.checks.append(CheckResult(token_type=TokenType.UP, value=None, verdict=False))
    else:
        upper_element = (i-1, j)
        value = matrix[i-1][j]
        result = _check_element(upper_element, matrix)
        if not result:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=False))
        else:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=True))
    
def _check_down_token(token: Token, matrix: List[List[str]]) -> None:
    i, j = token.element[0], token.element[1]
    if i == len(matrix) - 1:
        token.checks.append(CheckResult(token_type=TokenType.DOWN, value=None, verdict=False))
    else:
        lower_element = (i+1, j)
        value = matrix[i+1][j]
        result = _check_element(lower_element, matrix)
        if not result:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=False))
        else:
            token.checks.append(CheckResult(token_type=TokenType.NORMAL, value=value, verdict=True))

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
    from logging import basicConfig, DEBUG, INFO
    basicConfig(level=DEBUG)
    VERBOSE = True
    matrix = _open_matrix("input.txt")
    all_partnumbers = _find_matrix_partnumbers(matrix)
    all_checked_partnumbers = []
    for partnumber in all_partnumbers:
        if checked_partnumber := _scan_partnumber(partnumber, matrix):
            logger.debug(f"\t {repr(checked_partnumber)}")
            all_checked_partnumbers.append(checked_partnumber.value())
    logger.info(all_checked_partnumbers)
    logger.info(sum(all_checked_partnumbers))
    
    
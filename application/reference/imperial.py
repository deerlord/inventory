from functools import reduce
from operator import mul, truediv
from typing import List, Tuple

DRY_MEASUREMENTS = [
    (1, "tsp"),
    (3, "tbsp"),
    (16, "cup"),
]


LIQUID_MEASUREMENTS = [(1, "oz"), (8, "cup"), (2, "pint"), (2, "quart"), (4, "gallon")]


def convert(measure: List[Tuple[int, str]], amount: int, m: str, to: str):
    factors = [i[0] for i in measure]
    measures = [i[1] for i in measure]
    if m not in measures or to not in measures:
        return False
    s_index = measures.index(m)
    e_index = measures.index(to)
    if s_index > e_index:
        _ = e_index
        e_index = s_index
        s_index = _
        op = mul
    else:
        op = truediv
    factor = reduce(mul, factors[s_index + 1 : e_index + 1])
    return op(amount, factor)

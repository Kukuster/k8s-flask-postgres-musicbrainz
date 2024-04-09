from typing import Dict, List, Any, NamedTuple, Union, Tuple, TypeVar

T = TypeVar("T")
def flatten_list_of_lists(matrix: List[List[T]]) -> List[T]:
    flat_list: List[T] = []
    for row in matrix:
        flat_list += row
    return flat_list

def ms_to_durationstr(ms: int) -> str:
    """Convert milliseconds to a string in the format mm:ss"""
    return f"{ms // 60000}:{ms % 60000 // 1000 :02d}"

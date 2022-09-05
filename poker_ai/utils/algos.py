from typing import Any, List
import math

def rotate_list(l: List[Any], n: int):
    """Helper function for rotating lists, typically list of Players

    Parameters
    ----------
    l : List[Any]
        List to rotate.
    n : int
        Integer index of where to rotate.
    """
    if n > len(l):
        raise ValueError
    return l[n:] + l[:n]

def round_to_nearest_n(val, n):
    math.floor(val / n) * n

def rank_rounding(x:int):
    """Rounding function for treys rank."""

    if x<100:
        return x 
    elif x<1000:
        return round_to_nearest_n(x,10) 
    else:
        return round_to_nearest_n(x,100)

from typing import Any, List
import math
import bisect
import random

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
    return math.floor(val / n) * n

def rank_rounding(x:int):
    """Rounding function for treys rank."""

    return round_to_nearest_n(x,100) 

def round_to_nearest_element(num,rangeList= [0.0,0.1,0.3,0.5,0.7]):
    beg = bisect.bisect_right(rangeList,num)
    if rangeList[beg-1] == num: #Handle Perfect Hit Edge Case
        return num
    elif not beg: #Left Edge Case
        return rangeList[0]
    elif beg == len(rangeList): #Right Edge Case
        return rangeList[-1]
    else:
        if num - rangeList[beg-1] <= rangeList[beg] - num:
            return rangeList[beg-1]
        else:
            return rangeList[beg]

def randomly_move_amounts_in_list(l, times, step=400):
    index=list(range(len(l)))
    for i in range(times):
        loc=random.choices(index, k=2)
        if l[loc[0]] > step*2:
            l[loc[0]]=l[loc[0]]-step
            l[loc[1]]=l[loc[1]]+step
    return l
from math import cos
from math import sin


def rotate_around(point, pivot, radians):
    """
        Rotatoes point around pivot by radians
    """
    c = cos(radians)
    s = sin(radians)
    
    return [c * (point[0] - pivot[0]) - s * (point[1] - pivot[1]) + pivot[0],
     s * (point[0] - pivot[0]) + c * (point[1] - pivot[1]) + pivot[1]]

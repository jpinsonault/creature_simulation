from math import cos
from math import sin


def rotate_around(cos_radians, sin_radians, point, pivot, radians):
    """
        Rotatoes point around pivot by radians
    """

    p0 = point[0] - pivot[0]
    p1 = point[1] - pivot[1]
    return [cos_radians* p0 - sin_radians* p1 + pivot[0], sin_radians* p0 + cos_radians* p1 + pivot[1]]


def rotate_shape(cos_radians, sin_radians, shape, pivot, radians):
    """
        Rotatoes point around pivot by radians
    """
    length = len(shape)
    index = 0
    rotated_shape = []

    while index < length:
        p0 = shape[index][0] - pivot[0]
        p1 = shape[index][1] - pivot[1]
        rotated_shape.append([cos_radians* p0 - sin_radians* p1 + pivot[0], sin_radians* p0 + cos_radians* p1 + pivot[1]])
        index += 1

    return rotated_shape

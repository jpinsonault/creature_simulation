def rotate_around(float cos_radians, float sin_radians, point, pivot, float radians):
    """
        Rotates point around pivot by radians
    """
    cdef float s0_minus_p0
    cdef float s1_minus_p1
    cdef float p0
    cdef float p1

    p0 = pivot[0]
    p1 = pivot[1]
    s0_minus_p0 = point[0] - p0
    s1_minus_p1 = point[1] - p1

    return [cos_radians* s0_minus_p0 - sin_radians* s1_minus_p1 + p0, sin_radians* s0_minus_p0 + cos_radians* s1_minus_p1 + p1]


def rotate_shape(float cos_radians, float sin_radians, shape, pivot, float radians):
    """
        Rotatoes a list of points around pivot by radians
    """
    cdef int length = len(shape)
    cdef index = 0
    rotated_shape = []
    cdef float s0_minus_p0
    cdef float s1_minus_p1
    cdef float p0
    cdef float p1

    for index in range(length):
        p0 = pivot[0]
        p1 = pivot[1]
        s0_minus_p0 = shape[index][0] - p0
        s1_minus_p1 = shape[index][1] - p1
        rotated_shape.append([cos_radians* s0_minus_p0 - sin_radians* s1_minus_p1 + p0, sin_radians* s0_minus_p0 + cos_radians* s1_minus_p1 + p1])

    return rotated_shape

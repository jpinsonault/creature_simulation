from libc.math cimport abs as abs_c
from libc.math cimport sqrt
from itertools import chain

import numpy as np
cimport numpy as np
from cpython cimport bool


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



#######################################
# Collision detection functions
#######################################

# utility functions
cdef double dot_2d(double [:] first, double [:] second):
    """Returns the dot product of two vectors"""

    return first[0] * second[0] + first[1] * second[1]


# _perp = lambda (x, y): [-y, x]                          # perpendicular
cdef double* _perp(double [:] vector):
    cdef double[2] perp_vector
    perp_vector[0] = -vector[0]
    perp_vector[1] = vector[1]

    return perp_vector


# _mag = lambda (x, y): sqrt(x * x + y * y)               # magnitude, or length
cdef _mag(double [:] vector):
    cdef double x = vector[0]
    cdef double y = vector[1]

    return sqrt(x * x + y * y)

# _normalize = lambda V: [i / _mag(V) for i in V]         # normalize a vector
cdef double* _normalize(double [:] vector):
    cdef double[2] normalized
    cdef double magnitude = _mag(vector)
    normalized[0] = vector[0] / magnitude
    normalized[1] = vector[1] / magnitude

    return normalized

# _intersect = lambda A, B: (A[1] > B[0] and B[1] > A[0]) # intersection test
cdef inline bool _intersect(double [:] A, double [:] B):
    return (A[1] > B[0] and B[1] > A[0])
cdef inline double _min(double first, double second):
    if first < second:
        return first
    else:
        return second


cdef inline double _max(double first, double second):
    if first > second:
        return first
    else:
        return second


cdef inline double _min_vector(double [:] vector):
    cdef int index

    cdef double min_found = vector[0]

    for index in range(vector.shape[0]):
        min_found = _min(min_found, vector[index])

    return min_found


cdef inline double _max_vector(double [:] vector):
    cdef int index

    cdef double max_found = vector[0]

    for index in range(vector.shape[0]):
        max_found = _max(max_found, vector[index])

    return max_found


cdef _project(double [:,:] points, double [:] axis, double* output):
    """project self onto axis"""
    cdef int index

    cdef double [:] point
    cdef double projected_point
    cdef double min_found
    cdef double max_found

    projected_point = dot_2d(points[0], axis)

    min_found = projected_point
    max_found = projected_point

    for index in range(1, points.shape[0]):
        projected_point = dot_2d(points[index], axis)
        min_found = _min(min_found, projected_point)
        max_found = _max(max_found, projected_point)

    # return the span of the projection
    output[0] = min_found
    output[1] = max_found


class PolygonCython(object):
    """"""
    def collide_bounds(self, second):
        self_bounds = self.get_bounds()
        cdef int a_x = self_bounds[0]
        cdef int a_y = self_bounds[1]
        cdef int a_w = self_bounds[2]
        cdef int a_h = self_bounds[3]

        second_bounds = second.get_bounds()
        cdef int b_x = second_bounds[0]
        cdef int b_y = second_bounds[1]
        cdef int b_w = second_bounds[2]
        cdef int b_h = second_bounds[3]

        a_w = a_w / 2
        a_h = a_h / 2

        a_x = a_x + a_w
        a_y = a_y + a_h

        return ((abs_c(a_x - b_x) < (a_w + b_w)) and
               (abs_c(a_y - b_y) < (a_h + b_h)))

    def collide_poly(self, other):
        """
        test if other polygon collides with self using seperating axis theorem
        if collision, return projections
        """
        # a projection is a vector representing the span of a polygon projected
        # onto an axis
        # projections = []

        self.calc_shape_rotation()
        other.calc_shape_rotation()

        cdef int self_num_points = self.num_points
        cdef int other_num_points = other.num_points
        cdef double[:,:] self_points = np.array(self.absolute_shape)
        cdef double[:,:] other_points = np.array(other.absolute_shape)

        cdef double [:] point
        cdef double [:] next_point
        cdef double [2] edge
        cdef double [2] axis
        cdef double [2] self_projection
        cdef double [2] other_projection
        cdef int num_points

        cdef double magnitude

        cdef int index
        for index in range(self_num_points + other_num_points):
            # Make the edge
            if index < self_num_points:
                point = self_points[index]
                num_points = self_num_points
                next_point = self_points[(index + 1) % num_points]
            else:
                point = other_points[index - self_num_points]
                num_points = other_num_points
                next_point = other_points[((index - self_num_points) + 1) % num_points]

            edge[0] = point[0] - next_point[0]
            edge[1] = point[1] - next_point[1]

            # Normalize
            magnitude = _mag(edge)
            edge[0] /= magnitude
            edge[1] /= magnitude

            # Get perpendicular axis
            axis[:] = edge
            axis[0] *= -1

            # Project both shapes onto axis
            _project(self_points, axis, self_projection)
            _project(other_points, axis, other_projection)

            if not _intersect(self_projection, other_projection):
                return False

        return True

        # for edge in chain(self._make_edges(), other._make_edges()):
        #     edge = _normalize(edge)
        #     # the separating axis is the line perpendicular to the edge
        #     axis = _perp(edge)
        #     self_projection = self.project(axis)
        #     other_projection = other.project(axis)
        #     # if self and other do not intersect on any axis, they do not
        #     # intersect in space
        #     if not _intersect(self_projection, other_projection):
        #         return False
            # find the overlapping portion of the projections
            # projection = self_projection[1] - other_projection[0]
            # projections.append((axis[0] * projection, axis[1] * projection))
        # return projections
        # return True

    def _make_edges(self):
        points = self.absolute_shape

        for i, point in enumerate(points):
            next_point = points[(i + 1) % self.num_points] # x, y of next point in series
            # yield [point, next_point]
            yield [point[0] - next_point[0], point[1] - next_point[1]]

    def project(self, axis):
        """project self onto axis"""
        points = self.absolute_shape
        projected_points = [dot_2d(point, axis) for point in points]
        # return the span of the projection
        return min(projected_points), max(projected_points)

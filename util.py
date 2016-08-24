import typing
from typing import List


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return "x: %r y: %r" % (self.x, self.y)

    def move(self, direction: 'Direction'):
        """Modifies the Position in place.
        Returns the position for function chaining"""
        self.x += direction.dx
        self.y += direction.dy
        return self

    def direction_to(self, target: 'Position') -> 'Direction':
        return Direction(target.x - self.x, target.y - self.y)

    def copy(self):
        return Position(self.x, self.y)

    def update(self, other: 'Position'):
        """Copies Coordinates from other Position into this one."""
        self.x, self.y = other.x, other.y

    def to_tuple(self) -> typing.Tuple[int, int]:
        return self.x, self.y

    def distance(self, other: 'Position') -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def circle(self, radius: int) -> List['Position']:
        """Returns a circle around this Position.
        radius must be >= 1"""
        circle_list = []  # type: List[Position]

        y = self.y + radius
        for x in range(self.x - radius, self.x + radius + 1):
            circle_list.append(Position(x, y))

        y = self.y - radius
        for x in range(self.x - radius, self.x + radius + 1):
            circle_list.append(Position(x, y))

        x = self.x + radius
        for y in range(self.y - radius + 1, self.y + radius):
            circle_list.append(Position(x, y))

        x = self.x - radius
        for y in range(self.y - radius + 1, self.y + radius):
            circle_list.append(Position(x, y))

        return circle_list

    def neighbors(self):
        """Returns the 8 surrounding Positions of this Position."""
        return self.circle(1)

    def line_to(self, goal: 'Position') -> List['Position']:
        line = []  # type: List['Position']
        for x, y in _bresenham(self.to_tuple(), goal.to_tuple()):
            line.append(Position(x, y))
        return line


class Direction:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy


class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.xe = x + w
        self.ye = y + h

    def in_bounds(self, pos):
        return (self.x <= pos.x < self.xe and
                self.y <= pos.y < self.ye)


def _bresenham(start: typing.Tuple[int, int], end: typing.Tuple[int, int]
               ) -> typing.List[typing.Tuple[int, int]]:
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    Taken from:
    http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
 
    >>> points1 = _bresenham((0, 0), (3, 4))
    >>> points2 = _bresenham((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print (points1)
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print (points2)
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

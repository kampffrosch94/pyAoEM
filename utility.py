import typing


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

    def apply_direction(self, direction: 'Direction'):
        """Modifies the Position in place.
        Returns the position for function chaining"""
        self.x += direction.dx
        self.y += direction.dy
        return self

    def copy(self):
        return Position(self.x, self.y)

    def to_tuple(self) -> typing.Tuple[int, int]:
        return self.x, self.y

    def distance(self, other: 'Position') -> int:
        return pos_distance(self, other)

    def neighbors(self):
        """Yields the 8 surrounding Positions of this Position."""
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == 0 and dy == 0):
                    yield Position(self.x + dx, self.y + dy)


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


def pos_distance(start: Position, end: Position) -> int:
    return max(abs(start.x - end.x), abs(start.y - end.y))


def get_line(start: typing.Tuple[int, int], end: typing.Tuple[int, int]
             ) -> typing.List[typing.Tuple[int, int]]:
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    Taken from:
    http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
 
    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
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

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x,self.y))

    def __eq__(self,other):
        return (self.x,self.y) == (other.x,other.y)

    def __repr__(self):
        return ("x: %r y: %r" % (self.x,self.y))

    def apply_direction(self,direction):
        self.x += direction.dx
        self.y += direction.dy

    def copy(self):
        return Position(self.x,self.y)

    def to_tuple(self):
        return (self.x,self.y)

class Direction:
    def __init__(self,dx,dy):
        self.dx = dx
        self.dy = dy

class Rectangle:
    def __init__(self,x,y,w,h):
        self.x  = x
        self.y  = y
        self.xe = x + w
        self.ye = y + h

    def in_bounds(self,pos):
        return (pos.x >= self.x and pos.x < self.xe and
                pos.y >= self.y and pos.y < self.ye)

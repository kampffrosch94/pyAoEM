class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x,self.y))

    def __eq__(self,other):
        return (self.x,self.y) == (other.x,other.y)

class Rectangle:
    def __init__(self,x,y,w,h):
        self.x  = x
        self.y  = y
        self.xe = x + w
        self.ye = y + h

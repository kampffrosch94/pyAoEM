import uuid
import inspect
from sdl2 import *
from sdl2.sdlimage import *
"""Entity Component System"""

class Entity(object):
    def __init__(self,world):
        self.id = hash(uuid.uuid4())
        self.world = world
        world.entities.add(self)

    def __hash__(self):
        return self.id

    def __str__(self):
        result =         "Entity(id = %r" % self.id
        for e in self:
            result += "\n       %s = %r" % (e,
                    self.world.components[e][self])
        result += ")"
        return result

    def __repr__(self):
        return  "Entity(id = %r)" % self.id

    def __iter__(self):
        for ct in self.world.componenttypes :
            if self in self.world.components[ct]:
                yield ct

    def __getattr__(self, name):
        """Gets the component data related to the Entity."""
        if name in ("id", "world"):
            return object.__getattr__(self, name)
        if not name in self.world.componenttypes:
            raise AttributeError("object '%r' has no attribute '%r'" % \
                (self.__class__.__name__, name))
        return self.world.components[name][self]

    def __setattr__(self, name, value):
        """Sets the component data related to the Entity."""
        if name in ("id", "world"):
            object.__setattr__(self, name, value)
        else:
            wctypes = self.world.componenttypes
            if name not in self.world.componenttypes:
                self.world.componenttypes.add(name)
                self.world.components[name] = {}
            self.world.components[name][self] = value
            self.world.system_entity_cache_useable.clear()

    def __delattr__(self, name):
        """Deletes the component data related to the Entity."""
        if name in ("id", "world"):
            raise AttributeError("'%s' cannot be deleted.", name)
        try:
            ctype = self.world.componenttypes[name]
        except KeyError:
            raise AttributeError("object '%s' has no attribute '%s'" % \
                (self.__class__.__name__, name))
        del self.world.components[ctype][self]

    def set(self,attribute):
        self.__setattr__(attribute.__class__.__name__,attribute)

    def get(self, classobject):
        return self.__getattr__(classobject.__name__)

    def delete(self):
        """Removes the Entity from the world it belongs to."""
        self.world.delete(self)

class World(object):
    def __init__(self):
        self.systems = {}
        self.system_entity_cache = {}
        self.system_entity_cache_useable = []
        self.entities = set()
        self.components = {}
        self.componenttypes = set()

        SDL_Init(SDL_INIT_VIDEO)
        IMG_Init(IMG_INIT_JPG)
        self.window = SDL_CreateWindow(b"Test",0,0,640,640,
                                       SDL_SWSURFACE);

        self.alive = True

    def delete(self, entity):
        """Removes an Entity from the World, including all its data."""
        for ct in self.componenttypes:
            if entity in self.components[ct]:
                c = self.components[ct][entity]
                if hasattr(c,"destroy") and hasattr(c.destroy,"__call__"):
                    c.destroy()
                del self.components[ct][entity]
        self.entities.remove(entity)
        self.system_entity_cache_useable.clear()

    def add_system(self,system):
        if not isinstance(system,System):
            raise ValueError("Only instances of System are allowed.")
        name = system.__class__.__name__
        if name in self.systems.keys():
            raise KeyError("A system of this name is already registered.")
        self.systems[name] = system


    def invoke_system(self,systemclass):
        def find_matching_entities(typerestriction):
            def condition(typerestriction,entity):
                ecs = set(ec for ec in entity)
                return typerestriction.issubset(ecs)
            return {e for e in self.entities 
                    if condition(typerestriction,e)}
        systemname = systemclass.__name__
        s = self.systems[systemname]
        if s.active:
            if (systemname in self.system_entity_cache_useable):
                s.process(self.system_entity_cache[systemname])
            else:
                me = find_matching_entities(s.componenttypes)
                s.process(me)
                self.system_entity_cache[systemname] = me
                self.system_entity_cache_useable.append(systemname) 

    def end(self):
        self.alive = False

    def destroy(self):
        entities = self.entities.copy() #avoid del in the list we are
                                        #operating on
        for entity in entities:
            self.delete(entity)

        for key,system in self.systems.items():
            if hasattr(system,"destroy") and hasattr(
                    system.destroy,"__call__"):
                system.destroy()

        SDL_DestroyWindow(self.window)
        SDL_Quit()
            
class System(object):
    """System which runs the code in a world.

    componenttypes is a list of components an entity must have to
    be processed by this system.

    process() is called by the world when it makes a step. It get's
    all the matching entities as parameter.
    
    if active==False then process() wont be called"""

    def __init__(self,componentclasses = []):
        self.componenttypes = set(c.__name__ for c in componentclasses)
        self.active = True

    def process(self,entities):
        raise NotImplementedError("Must be implemented by a Subclass.")


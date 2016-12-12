import uuid
import logging
import animation
import base.data

import map_
from typing import Optional

"""Entity Component System"""

event_logger = logging.getLogger("Event")

ecs_logger = logging.getLogger("ECS")
ecs_logger.disabled = True


class Entity:
    def __init__(self, world):
        self.id = hash(uuid.uuid4())
        self.world = world  # type: World
        world.entities.append(self)

    def __hash__(self):
        return self.id

    def __str__(self):
        result = "Entity(id = %r" % self.id
        for e in self:
            result += "\n       %s = %r" % (e,
                                            self.world.components[e][self])
        result += ")"
        return result

    def __repr__(self):
        if hasattr(self, "name"):
            return "Entity(%s)" % self.name
        return "Entity(id = %r)" % self.id

    def __iter__(self):
        for ct in self.world.componenttypes:
            if self in self.world.components[ct]:
                yield ct

    def components(self):
        for ct in self:
            yield self.world.components[ct][self]

    def event_handlers(self, event):
        h_components = []
        h_name = event.handler_name
        for c in self.components():
            if hasattr(c, h_name) and callable(getattr(c, h_name)):
                h_components.append(c)
        h_components.sort(key=(lambda c: c.priority), reverse=True)
        for c in h_components:
            yield c

    def handle_event(self, event):
        event_logger.debug("%r handles %s" % (self, event))
        h_name = event.handler_name
        for c in self.event_handlers(event):
            event_logger.debug("component: %r handles %s" % (c, event))
            getattr(c, h_name)(event)
        event_logger.debug("result: %s" % event)

    def __getattr__(self, name):
        """Gets the component data related to the Entity."""
        if name is "id":
            return self.id
        if name is "world":
            return self.world
        if (not name in self.world.componenttypes) or (
                not self in self.world.components[name]):
            if name != "name":
                entity_name = self.name
            else:
                entity_name = self.id
            raise AttributeError("entity %r has no attribute %r" %
                                 (entity_name, name))
        return self.world.components[name][self]

    def __setattr__(self, name, value):
        """Sets the component data related to the Entity."""
        if name in ("id", "world"):
            object.__setattr__(self, name, value)
        else:
            if name not in self.world.componenttypes:
                self.world.componenttypes.add(name)
                self.world.components[name] = {}
            if self in self.world.components[name]:
                raise AttributeError("%s is already an attribute of %r" %
                                     (name, self))
            self.world.components[name][self] = value

            system_keys = self.world.find_entity_systems_wct(self, name)
            for sk in system_keys:
                self.world.system_entities[sk].append(self)

    def __delattr__(self, name):
        """Deletes the component data related to the Entity."""
        if name in ("id", "world"):
            raise AttributeError("'%s' cannot be deleted.", name)
        if not self in self.world.components[name]:
            raise AttributeError("Entity '%r' has no attribute '%s'" % \
                                 (self.id, name))

        c = self.world.components[name][self]

        system_keys = self.world.find_entity_systems_wct(self, name)
        for sk in system_keys:
            self.world.system_entities[sk].remove(self)
            ecs_logger.debug("Deleted %s from %s" % (self.id, sk))

        del self.world.components[name][self]
        ecs_logger.debug("Deleted %s from %s" % (name, self.id))

    def set(self, attribute):
        self.__setattr__(attribute.__class__.__name__, attribute)

    def get(self, classobject):
        return self.__getattr__(classobject.__name__)

    def delete(self, classobject):
        return self.__delattr__(classobject.__name__)

    def hasattr(self, name):
        """Don't check for world or id."""
        if (name in self.world.componenttypes) and (
                    self in self.world.components[name]):
            return True
        else:
            return False

    def has(self, classobject):
        """Don't check for world or id."""
        name = classobject.__name__
        return self.hasattr(name)

    def remove(self):
        """Removes the Entity from the world it belongs to."""
        self.world.remove_entity(self)

    @property
    def identifier(self):
        if hasattr(self, "name"):
            return self.name
        else:
            return self.id


class World(object):
    def __init__(self):
        self.entities = []
        self.components = {}
        self.componenttypes = set()

        self.systems = {}
        self.system_entities = {}
        # The keys of systems which use a certain componenttype
        self.componenttypes_to_system = {}

        self.alive = True
        self.main_loop = None

        self.map = None  # type: Optional[map_.TileMap]
        self.animation_q = []  # type: List[animation.Animation]

        self.base = base.data.BaseInfo()

    def remove_entity(self, entity):
        """Removes an Entity from the World, including all its data."""
        for ct in entity:
            entity.__delattr__(ct)
        self.entities.remove(entity)

    def add_system(self, system):
        if not isinstance(system, System):
            raise ValueError("Only instances of System are allowed.")
        key = system.__class__.__name__
        if key in self.systems:
            raise KeyError("A system of this name is already registered.")

        self.systems[key] = system
        for ct in system.componenttypes:
            if not ct in self.componenttypes_to_system:
                self.componenttypes_to_system[ct] = []
            self.componenttypes_to_system[ct].append(key)

        if len(system.componenttypes) > 0:
            self.system_entities[key] = self.find_system_entities(system)
        else:
            self.system_entities[key] = []
        return system

    def find_system_entities(self, system):
        typerestriction = system.componenttypes

        def condition(type_restr, entity):
            ecs = [ec for ec in entity]  # all component_ts of entity
            return type_restr.issubset(ecs)

        return [e for e in self.entities if condition(typerestriction, e)]

    def get_system_entities(self, system_class):
        key = system_class.__name__
        return self.system_entities[key]

    def find_entity_systems_wct(self, entity, ct):
        ecs = [ec for ec in entity]  # all component_ts of entity
        return [key for key in self.systems
                if (ct in self.systems[key].componenttypes) and
                self.systems[key].componenttypes.issubset(ecs)]

    def invoke_system(self, systemclass):
        key = systemclass.__name__
        s = self.systems[key]
        se = self.system_entities[key]
        ecs_logger.debug(se)
        if s.active:
            s.process(se[:])  # copy to prevent modification bugs

    def end(self):
        self.alive = False

    def destroy(self):
        entities = self.entities.copy()  # avoid del in the list we are
        # operating on
        for entity in entities:
            self.remove_entity(entity)

        for key, system in self.systems.items():
            if hasattr(system, "destroy") and hasattr(
                    system.destroy, "__call__"):
                system.destroy()


class System:
    """System which runs the code in a world.

    componenttypes is a list of components an entity must have to
    be processed by this system.

    process() is called by the world when it makes a step. It get's
    all the matching entities as parameter.
    
    if active==False then process() wont be called"""

    def __init__(self, componentclasses=None):
        if componentclasses is None:
            componentclasses = []
        self.componenttypes = set(c.__name__ for c in componentclasses)
        self.active = True

    def process(self, entities):
        raise NotImplementedError("Must be implemented by a Subclass.")

    def __hash__(self):
        return hash(self.__class__.__name__)

class TakeDamage(object):
    def __init__(self, dmg_event):
        self.amount = dmg_event.amount
        self.handler_name = "take_damage"

class DealDamage(object):
    def __init__(self, amount=0):
        self.amount = amount
        self.handler_name = "deal_damage"

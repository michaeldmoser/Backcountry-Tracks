

class UserGearService(object):

    def __init__(self, inventory):
        self.inventory = inventory

    def create(self, owner, obj):
        inventory = self.inventory(owner)
        piece_o_gear = inventory.PieceOfGear(obj)
        inventory.add_gear(piece_o_gear)

        return piece_o_gear

    def update(self, owner, obj_id, obj):
        return {}

    def delete(self, owner, obj_id):
        pass

    def list(self, owner):
        return []

    def get(self, obj_id):
        return None


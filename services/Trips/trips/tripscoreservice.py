
class TripsCoreService(object):

    def __init__(self, catalog):
        self.catalog = catalog

    def create(self, owner, obj):
        catalog = self.catalog(owner)
        trip = catalog.Item(obj)
        catalog.add_item(trip)

        return trip 

    def update(self, owner, obj_id, obj):
        return {}

    def delete(self, owner, obj_id):
        catalog = self.catalog(owner)
        catalog.delete(obj_id)

    def list(self, owner):
        catalog = self.catalog(owner)
        items = catalog.list_items()
        return items

    def get(self, obj_id):
        return None



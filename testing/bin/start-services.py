#!/usr/bin/env python
from tptesting import environment
environ = environment.create()
environ.make_pristine()
environ.bringup_infrastructure()

douglas = environ.douglas
douglas.mark_registered()
environ.create_user(douglas)

ramona = environ.ramona
ramona.mark_registered()
environ.create_user(ramona)

albert = environ.albert
albert.mark_registered()
environ.create_user(albert)

environ.trips.add_trips_to_user(douglas, environ.data['trips'])
environ.gear.add_gear_to_user(douglas, environ.data['gear'])



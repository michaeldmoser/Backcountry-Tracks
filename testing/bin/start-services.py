from tptesting import environment
environ = environment.create()
environ.make_pristine()
environ.bringup_infrastructure()

douglas = environ.douglas
douglas.mark_registered()
environ.create_user(douglas)

for trip in environ.data['trips']:
    environ.trips.add(owner=douglas.email, **trip)



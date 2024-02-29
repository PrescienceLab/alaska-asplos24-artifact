import os


spec_locations = [
    "./SPEC2017.tar.gz",
    "~/SPEC2017.tar.gz",
    "/SPEC2017.tar.gz",
]
def find_spec():
    print('looking for SPEC in these locations:', spec_locations)
    for loc in spec_locations:
        loc = os.path.expanduser(loc)
        if os.path.isfile(loc):
            return loc
    return None



import comma

SOME_CSV_STRING = "name,age,gender\nPerson1,33,M\nPerson2,25,M\n"


def test_slicing_parent():

    obj = comma.load(SOME_CSV_STRING)

    # make sure we know what we are getting
    assert len(obj) == 2
    assert obj.header is not None
    assert len(obj.header) == 3

    # get reference to parent object
    assert obj._parent is not None
    ref_id = id(obj._parent)

    # check this is propagated to slices
    # use hex(id(...)) to get an easier to read number
    assert (ref_id == id(obj[0]._parent))
    assert (ref_id == id(obj[0:10]._parent))
    assert (ref_id == id(obj[0:10][0]._parent))



import copy
import typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "CloneableCollection"
]


class CloneableCollection(object):
    """
    An abstract collection (containing a `data` attribute, for instance, from
    `collections.UserList` or `collections.UserDict`) that can be cloned with
    new data.
    """

    # noinspection PyMethodMayBeStatic
    def _validate_newdata(self, newdata: typing.Any = None) -> bool:
        """
        Returns `True` if the provided `newdata` is acceptable as the internal
        state of the collection. This protected helper method is called by
        `CloneableCollection.clone()` to ensure the new data provided for a
        cloned object will not lead the object to be an invalid internal state.
        """

        if newdata is None:
            return True

        return True

    def clone(self, newdata: typing.Any = None, **kwargs):
        """
        Returns a clone of the current collection, with possible different
        underlying data, as specified by `newdata`.
        """

        if not hasattr(self, "data"):
            raise Exception(
                "for a class to be a `ClonableCollection`, it must at"
                "at least have a `data` attribute"
            )

        if "data" in kwargs:
            raise ValueError(
                "use the `newdata` keyword too override existing data (that way "
                "the data is properly validated, unlike for all other overrides)"
            )

        # validate new data
        if not self._validate_newdata(newdata=newdata):
            raise ValueError("`newdata` failed internal validation")

        # create new class instance
        inst = self.__class__.__new__(self.__class__)

        # Copy all attributes except obj.data (handled separately)
        for key, value in self.__dict__.items():
            # kwargs can override existing attributes
            if key in kwargs:
                inst.__dict__ [key] = kwargs.get(key)

            # this is handled separately
            if key != "data":
                inst.__dict__[key] = value

        # Create a copy of the data and avoid triggering descriptors
        inst.__dict__["data"] = newdata or copy.deepcopy(self.__dict__["data"])

        return inst

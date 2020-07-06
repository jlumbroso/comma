
import functools
import os
import textwrap
import typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "settings"
]


class ConfigMetaclass(type):

    # ===================================================================
    # Metaclass bound functions

    @staticmethod
    def __bound__init__(self):
        """
        Returns a new configuration object.
        """
        # initialize metadata
        setattr(self, "_metadata", dict())

    @staticmethod
    def __bound_get(
            self,

            # partially bound by metaclass:
            field_name: str,
            field_type: type,
            field_env_name: str,
            field_doc: str,
            field_default: typing.Any,
    ):
        return ConfigHelper.parse(
            value=self._metadata.get(
                field_name,
                os.environ.get(field_env_name, field_default)),
            typ=field_type)

    @staticmethod
    def __bound_set(
            self,
            value,

            # partially bound by metaclass:
            field_name: str,
            field_type: type,
            field_env_name: str,
            field_doc: str,
            field_default: typing.Any,
    ):
        self._metadata[field_name] = value

    # ===================================================================

    @staticmethod
    def _make_property(field_name, field_default, field_doc):
        field_type = ConfigHelper.guess(field_default)
        field_doc = textwrap.dedent(field_doc)
        field_info = {
            "field_name"    : field_name,
            "field_env_name": "COMMA_{}".format(field_name.upper()),
            "field_default" : field_default,
            "field_type"    : field_type,
            "field_doc"     : field_doc,
        }
        return property(
            fget=functools.partial(ConfigMetaclass.__bound_get, **field_info),
            fset=functools.partial(ConfigMetaclass.__bound_set, **field_info),
            doc=field_doc)

    def __init__(cls, name, bases, attrs):

        # initialize constructor
        setattr(cls, "__init__", ConfigMetaclass.__bound__init__)

        # gather all attribute names that are not protected/private
        class_field_names = list(filter(
            lambda s: s[:1] != "_",
            cls.__dict__))

        # create properties
        for field_name in class_field_names:
            field_default, field_doc = cls.__dict__.get(field_name)
            setattr(
                cls,
                field_name,
                ConfigMetaclass._make_property(
                    field_name=field_name,
                    field_default=field_default,
                    field_doc=field_doc))


class ConfigHelper:

    @classmethod
    def check(cls, value, typ):
        if typ is str:
            return type(value) is str
        if typ is bool:
            return cls.is_likely_bool(value)
        if typ is int:
            return cls.is_int(value)
        if typ is float:
            return cls.is_float(value)
        return False

    @classmethod
    def guess(cls, value):
        if type(value) is not str:
            return type(value)
        else:
            if cls.is_int(value):
                return int
            if cls.is_float(value):
                return float
            if cls.is_likely_bool(value):
                return bool
            return str

    @classmethod
    def parse(cls, value, typ=None):
        if typ is None:
            typ = cls.guess(value)
        if typ is str:
            return value
        if typ is bool:
            return cls.parse_bool(value)
        if typ is int:
            return cls.parse_int(value)
        if typ is float:
            return cls.parse_float(value)
        return

    # ======================================================================

    BOOL_STR_FALSE = ["f", "0", "false", "False", ""]
    BOOL_STR_TRUE  = ["t", "1", "true", "True"]

    @classmethod
    def is_likely_bool(cls, value):
        if type(value) is str:
            return value in cls.BOOL_STR_FALSE or value in cls.BOOL_STR_TRUE
        return type(value) is int or type(value) is bool

    @classmethod
    def parse_bool(cls, value):
        if type(value) is str:
            if value in cls.BOOL_STR_FALSE:
                return False
            if value in cls.BOOL_STR_TRUE:
                return True
            return bool(value)
        if type(value) is int:
            return not (value == 0)
        if type(value) is bool:
            return value
        return bool(value)

    @staticmethod
    def is_int(value):
        try:
            int(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    @staticmethod
    def parse_int(value):
        return int(value)

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except TypeError:
            return False
        except ValueError:
            return False

    @staticmethod
    def parse_float(value):
        return float(value)


class ConfigClass(metaclass=ConfigMetaclass):
    """
    Global configuration for the `comma` package; this helps influence some of the
    design choices of the library.
    """

    SLICE_DEEP_COPY_DATA = False, """
        Determines whether the slice of a `CommaTable` or `CommaRow` copies
        the underlying data or not. (Python convention suggests a slice should
        make a copy, however it may useful to circumvent this for convenience.)
        """

    SLICE_DEEP_COPY_PARENT = False, """
        Determines whether the slice of a `CommaTable` or `CommaRow` copies
        the reference to the parent `CommaFile` or duplicates the object. This
        affects whether changes to the header are propagated from the slice to
        the original dataset or not.
        """


settings = ConfigClass()

def get_full_class_name(cls):
    """
    Returns the full name of a class, including the module name.

    :param cls: The class.
    :return: The full name of the class
    """
    return cls.__module__ + "." + cls.__name__


def recursive_subclasses(cls):
    """
    :param cls: The class.
    :return: A list of the classes subclasses.
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in recursive_subclasses(s)]

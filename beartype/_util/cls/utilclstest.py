#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unmemoized class tester** (i.e., unmemoized and thus efficient
callable testing various properties of arbitrary classes) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilTypeException
from beartype._cave._cavefast import TestableTypes as TestableTypesTuple
from beartype._data.cls.datacls import TYPES_BUILTIN_FAKE
from beartype._data.mod.datamod import BUILTINS_MODULE_NAME
from typing import Tuple, Type, Union

# ....................{ HINTS                             }....................
TestableTypes = Union[type, Tuple[type, ...]]
'''
PEP-compliant type hint matching all **testable types** (i.e., types suitable
for use as the second parameter passed to the :func:`isinstance` and
:func:`issubclass` builtins).
'''

# ....................{ VALIDATORS                        }....................
def die_unless_type(
    # Mandatory parameters.
    cls: object,

    # Optional parameters.
    exception_cls: Type[Exception] = _BeartypeUtilTypeException,
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is a class.

    Parameters
    ----------
    cls : object
        Object to be validated.
    exception_cls : Type[Exception]
        Type of exception to be raised. Defaults to
        :exc:`_BeartypeUtilTypeException`.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is *not* a class.
    '''

    # If this object is *NOT* a class, raise an exception.
    if not isinstance(cls, type):
        assert isinstance(exception_cls, type), (
            'f{repr(exception_cls)} not exception class.')
        raise exception_cls(f'{repr(cls)} not class.')

# ....................{ TESTERS                           }....................
def is_type_subclass(cls: object, base_classes: TestableTypes) -> bool:
    '''
    ``True`` only if the passed object is a subclass of either the passed class
    if passed one class *or* at least one of the passed classes if passed a
    tuple of classes.

    Caveats
    ----------
    **This higher-level tester should always be called in lieu of the
    lower-level** :func:`issubclass` **builtin,** which raises an undescriptive
    exception when the first passed parameter is *not* a class: e.g.,

    .. code-block:: python

       >>> issubclass(object(), type)
       TypeError: issubclass() arg 1 must be a class

    This tester suffers no such deficits, instead safely returning ``False``
    when the first passed parameter is *not* a class.

    Parameters
    ----------
    obj : object
        Object to be inspected.
    base_classes : TestableTypes
        Class(es) to test whether this object is a subclass of defined as
        either:

        * A single class.
        * A tuple of one or more classes.

    Returns
    ----------
    bool
        ``True`` only if this object is a subclass of these class(es).
    '''
    assert isinstance(base_classes, TestableTypesTuple), (
        f'{repr(base_classes)} neither class nor tuple of classes.')

    # One-liners for tremendous bravery.
    return isinstance(cls, type) and issubclass(cls, base_classes)


def is_type_builtin(cls: type) -> bool:
    '''
    ``True`` only if the passed class is **builtin** (i.e., globally accessible
    C-based type requiring *no* explicit importation).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this class is builtin.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.mod.utilmodule import (
        get_object_type_module_name_or_none)

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # If this type is a fake builtin (i.e., type that is *NOT* builtin but
    # erroneously masquerading as being builtin), this type is *NOT* a builtin.
    # In this case, silently reject this type.
    if cls in TYPES_BUILTIN_FAKE:
        return False
    # Else, this type is *NOT* a fake builtin.

    # Fully-qualified name of the module defining this type if this type is
    # defined by a module *OR* "None" otherwise (i.e., if this type is
    # dynamically defined in-memory).
    cls_module_name = get_object_type_module_name_or_none(cls)

    # This return true only if this name is that of the "builtins" module
    # declaring all builtin types.
    return cls_module_name == BUILTINS_MODULE_NAME

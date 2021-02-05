#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype Least Recently Used (LRU) caching utilities.**

This private submodule implements supplementary cache-specific utility
functions required by various :mod:`beartype` facilities, including callables
generated by the :func:`beartype.beartype` decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilLRUCacheException

# ....................{ CLASSES                           }....................
#FIXME: This is currently completely untested. Add unit tests exhaustively
#exercising this class to a new
#"beartype_test.a00_unit.a00_util.cache.test_utilcachecall" submodule,
#including these pertinent edge cases:
#* Instantiating an "LRUCacheStrong(size=1)" and:
#  * Setting an arbitrary key-value pair on this cache.
#  * Setting another arbitrary key-value pair on this cache and validating that
#    the first such key-value pair no longer exists in this cache.
#  * Removing the last such key-value pair from this cache.
#* Instantiating an "LRUCacheStrong(size=2)" and:
#  * Setting two arbitrary key-value pairs on this cache: A and B.
#  * Validating that the first key-value pair of this cache is A.
#  * Setting another arbitrary key-value pair C on this cache.
#  * Validating that key-value pair A no longer exists in this cache.
#  * Validating that the first key-value pair of this cache is B.
#  * Getting key-value pair B.
#  * Validating that the first key-value pair of this cache is C.
#  * Setting key-value pair D on this cache and validating that key-value pair
#    C no longer exists in this cache.
#  * Validating that the first key-value pair of this cache is B.

class LRUCacheStrong(dict):
    '''
    **Strong Least Recently Used (LRU) cache** (i.e., a mapping from strong
    references to arbitrary keys onto strong references to arbitrary values,
    limited to some maximum positive number of key-value pairs by implicitly
    removing the least recently accessed key-value pair from this mapping on
    each attempt to set a new key-value pair on this mapping that would cause
    this mapping's size to exceed this number).

    Attributes
    ----------
    _size : int
        **Cache capacity** (i.e., maximum positive number of key-value pairs
        persisted by this cache).
    '''

    # ..................{ DUNDERS                           }..................
    def __init__(self, size: int) -> None:
        '''
        Initialize this cache to the empty dictionary.

        Parameters
        ----------
        size : int
            **Cache capacity** (i.e., maximum positive number of key-value
            pairs persisted by this cache).

        Raises
        ------
        _BeartypeUtilLRUCacheException
            If this capacity is either:

            * *Not* an integer.
            * A **non-positive integer** (i.e., either negative or zero).
        '''

        # If this size is *NOT* an integer, raise an exception.
        if not isinstance(size, int):
            raise _BeartypeUtilLRUCacheException(
                f'LRU cache capacity {repr(size)} not integer.')
        # Else, this size is an integer.
        #
        # If this size is non-positive, raise an exception.
        if size <= 0:
            raise _BeartypeUtilLRUCacheException(
                f'LRU cache capacity {size} not positive.')
        # Else, this size is positive.

        # Initialize our superclass to the empty dictionary.
        super().__init__()

        # Classify this parameter.
        self._size = size


    def __getitem__(
        self,
        key: 'Hashable',

        # Superclass methods efficiently localized as default parameters.
        __dict_delitem=dict.__delitem__,
        __dict_getitem=dict.__getitem__,
        __dict_setitem=dict.__setitem__,
    ) -> object:
        '''
        Value previously cached under the passed key if this key been recently
        cached *or* raise an exception otherwise (i.e., if this key has either
        not been previously cached *or* has but has since been removed due to
        not having been recently accessed).

        Specifically, this method (in order):

        * If this key has *not* been recently cached, raises the standard
          :class:`KeyError` exception.
        * Else:

          #. Gets the value previously cached under this key.
          #. Prioritizes this key by removing and re-adding this key back to
             the tail of this cache.
          #. Returns this value.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to retrieve the cached value of.

        Returns
        ----------
        object
            Arbitrary value recently cached under this key.

        Raises
        ----------
        TypeError
            If this key is unhashable.
        '''

        # Value cached under this key if this key has already been cached *OR*
        # raise the standard "KeyError" exception otherwise.
        value = __dict_getitem(self, key)

        # Prioritize this key by removing and re-adding this key back to the
        # tail of this cache.
        __dict_delitem(self, key)
        __dict_setitem(self, key, value)

        # Return this value.
        return value


    def __setitem__(
        self,
        key: 'Hashable',
        value: object,

        # Superclass methods efficiently localized as default parameters.
        __dict_hasitem=dict.__contains__,
        __dict_delitem=dict.__delitem__,
        __dict_setitem=dict.__setitem__,
        __dict_iter=dict.__iter__,
        __dict_len=dict.__len__,
    ) -> None:
        '''
        Cache the passed key-value pair while preserving LRU constraints.

        Specifically, this method (in order):

        #. If this key has already been cached, prioritize this key by removing
           this key from this cache.
        #. (Re-)add this key to the tail of this cache.
        #. If adding this key caused this cache to exceed its maximum capacity,
           silently remove the first (and thus least recently used) key-value
           pair from this cache.

        Parameters
        ----------
        key : Hashable
            Arbitrary hashable key to cache this value to.
        value : object
            Arbitrary value to be cached under this key.

        Raises
        ----------
        TypeError
            If this key is unhashable.
        '''

        # If this key has already been cached, prioritize this key by removing
        # this key from this cache *BEFORE* re-adding this key back below.
        if __dict_hasitem(self, key):
            __dict_delitem(self, key)

        # (Re-)add this key to the tail of this cache.
        __dict_setitem(self, key, value)

        # If adding this key caused this cache to exceed its maximum capacity,
        # silently remove the first (and thus least recently used) key-value
        # pair from this cache.
        if __dict_len(self) > self._size:
            __dict_delitem(self, next(__dict_iter(self)))

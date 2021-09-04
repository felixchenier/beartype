#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant code snippets** (i.e., triple-quoted
pure-Python code constants formatted and concatenated together into wrapper
functions implementing type-checking for decorated callables annotated by
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
#which are the optimal means of performing string formatting.

# ....................{ IMPORTS                           }....................
from beartype._decor._code.codesnip import (
    ARG_NAME_FUNC,
    ARG_NAME_RAISE_EXCEPTION,
    VAR_NAME_ARGS_LEN,
    VAR_NAME_PITH_ROOT,
    VAR_NAME_RANDOM_INT,
)
from inspect import Parameter

# ....................{ PITH                              }....................
PEP_CODE_PITH_ASSIGN_EXPR = (
    '''{pith_curr_var_name} := {pith_curr_expr}''')
'''
Python >= 3.8-specific assignment expression assigning the full Python
expression yielding the value of the current pith to a unique local variable,
enabling PEP-compliant child hints to obtain this pith via this efficient
variable rather than via this inefficient full Python expression.
'''


PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER = '?|PITH_ROOT_NAME`^'
'''
Placeholder source substring to be globally replaced by the **root pith name**
(i.e., name of the current parameter if called by the
:func:`pep_code_check_param` function *or* ``return`` if called by the
:func:`pep_code_check_return` function) in the parameter- and return-agnostic
code generated by the memoized :func:`pep_code_check_hint` function.

See Also
----------
:attr:`beartype._decor._code._pep._pephint.pep_code_check_hint`
:attr:`beartype._util.cache.utilcacheerror.EXCEPTION_CACHED_PLACEHOLDER`
    Related commentary.
'''

# ....................{ PARAM                             }....................
PARAM_KIND_TO_PEP_CODE_LOCALIZE = {
    # Snippet localizing any positional or keyword parameter as follows:
    #
    # * If this parameter's 0-based index (in the parameter list of the
    #   decorated callable's signature) does *NOT* exceed the number of
    #   positional parameters passed to the wrapper function, localize this
    #   positional parameter from the wrapper's variadic "*args" tuple.
    # * Else if this parameter's name is in the dictionary of keyword
    #   parameters passed to the wrapper function, localize this keyword
    #   parameter from the wrapper's variadic "*kwargs" tuple.
    # * Else, this parameter is unpassed. In this case, localize this parameter
    #   as a placeholder value guaranteed to *NEVER* be passed to any wrapper
    #   function: the private "__beartypistry" singleton passed to this wrapper
    #   function as a hidden default parameter and thus accessible here. While
    #   we could pass a "__beartype_sentinel" parameter to all wrapper
    #   functions defaulting to "object()" and then use that here instead,
    #   doing so would slightly reduce efficiency for no tangible gain. *shrug*
    Parameter.POSITIONAL_OR_KEYWORD: f'''
    # Localize this positional or keyword parameter if passed *OR* to the
    # sentinel value "__beartype_raise_exception" guaranteed to never be passed.
    {VAR_NAME_PITH_ROOT} = (
        args[{{arg_index}}] if {VAR_NAME_ARGS_LEN} > {{arg_index}} else
        kwargs.get({{arg_name!r}}, {ARG_NAME_RAISE_EXCEPTION})
    )

    # If this parameter was passed...
    if {VAR_NAME_PITH_ROOT} is not {ARG_NAME_RAISE_EXCEPTION}:''',

    # Snippet localizing any keyword-only parameter (e.g., "*, kwarg") by
    # lookup in the wrapper's variadic "**kwargs" dictionary. (See above.)
    Parameter.KEYWORD_ONLY: f'''
    # Localize this keyword-only parameter if passed *OR* to the sentinel value
    # "__beartype_raise_exception" guaranteed to never be passed.
    {VAR_NAME_PITH_ROOT} = kwargs.get({{arg_name!r}}, {ARG_NAME_RAISE_EXCEPTION})

    # If this parameter was passed...
    if {VAR_NAME_PITH_ROOT} is not {ARG_NAME_RAISE_EXCEPTION}:''',

    # Snippet iteratively localizing all variadic positional parameters.
    Parameter.VAR_POSITIONAL: f'''
    # For all passed positional variadic parameters...
    for {VAR_NAME_PITH_ROOT} in args[{{arg_index!r}}:]:''',
}
'''
Dictionary mapping from the type of each callable parameter supported by the
:func:`beartype.beartype` decorator to a PEP-compliant code snippet localizing
that callable's next parameter to be type-checked.
'''

# ....................{ RETURN                            }....................
PEP_CODE_CHECK_RETURN_PREFIX = f'''
    # Call this function with all passed parameters and localize the value
    # returned from this call.
    {VAR_NAME_PITH_ROOT} = {ARG_NAME_FUNC}(*args, **kwargs)

    # Noop required to artifically increase indentation level. Note that
    # CPython implicitly optimizes this conditional away - which is nice.
    if True:'''
'''
PEP-compliant code snippet calling the decorated callable and localizing the
value returned by that call.

Note that this snippet intentionally terminates on a line containing only the
``(`` character, enabling subsequent type-checking code to effectively ignore
indentation level and thus uniformly operate on both:

* Parameters localized via values of the :data:`PARAM_KIND_TO_PEP_CODE_LOCALIZE`
  dictionary.
* Return values localized via this sippet.

See Also
----------
https://stackoverflow.com/a/18124151/2809027
    Bytecode disassembly demonstrating that CPython optimizes away the spurious
   ``if True:`` conditional hardcoded into this snippet.
'''


PEP_CODE_CHECK_RETURN_SUFFIX = f'''
    return {VAR_NAME_PITH_ROOT}'''
'''
PEP-compliant code snippet returning from the wrapper function the successfully
type-checked value returned from the decorated callable.

Note that this snippet intentionally terminates on a line containing only the
``)`` character, which closes the corresponding character terminating the
:data:`PEP_CODE_GET_RETURN` snippet.
'''

# ....................{ HINT ~ placeholder : child        }....................
PEP_CODE_HINT_CHILD_PLACEHOLDER_PREFIX = '@['
'''
Prefix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''


PEP_CODE_HINT_CHILD_PLACEHOLDER_SUFFIX = ')!'
'''
Suffix of each **placeholder hint child type-checking substring** (i.e.,
placeholder to be globally replaced by a Python code snippet type-checking the
current pith expression against the currently iterated child hint of the
currently visited parent hint).
'''

# ....................{ HINT ~ placeholder : forwardref   }....................
PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX = '${FORWARDREF:'
'''
Prefix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''


PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX = ']?'
'''
Suffix of each **placeholder unqualified forward reference classname
substring** (i.e., placeholder to be globally replaced by a Python code snippet
evaluating to the currently visited unqualified forward reference hint
canonicalized into a fully-qualified classname relative to the external
caller-defined module declaring the currently decorated callable).
'''

# ....................{ HINT ~ hint : root                }....................
PEP_CODE_HINT_ROOT_PREFIX = f'''
        # Type-check this passed parameter or return value against this
        # PEP-compliant type hint.
        if not '''
'''
PEP-compliant code snippet prefixing all code type-checking the **root pith**
(i.e., value of the current parameter or return value) against the root
PEP-compliant type hint annotating that pith.

This prefix is intended to be locally suffixed in the
:func:`beartype._decor._code._pep._pephint.pep_code_check_hint` function by:

#. The value of the ``hint_child_placeholder`` local variable.
#. The :data:`PEP_CODE_HINT_ROOT_SUFFIX` suffix.
'''


PEP_CODE_HINT_ROOT_SUFFIX = f''':
            {ARG_NAME_RAISE_EXCEPTION}(
                func={ARG_NAME_FUNC},
                pith_name={PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER},
                pith_value={VAR_NAME_PITH_ROOT},{{random_int_if_any}}
            )
'''
'''
PEP-compliant code snippet suffixing all code type-checking the **root pith**
(i.e., value of the current parameter or return value) against the root
PEP-compliant type hint annotating that pith.

This snippet expects to be formatted with these named interpolations:

* ``{random_int_if_any}``, whose value is either:

  * If type-checking the current type hint requires a pseudo-random integer,
    :data:`PEP_CODE_HINT_ROOT_SUFFIX_RANDOM_INT`.
  * Else, the empty substring.

Design
----------
**This string is the only code snippet defined by this submodule to raise an
exception.** All other such snippets only test the current pith against the
current child PEP-compliant type hint and are thus intended to be dynamically
embedded in the conditional test initiated by the
:data:`PEP_CODE_HINT_ROOT_PREFIX` code snippet.
'''


PEP_CODE_HINT_ROOT_SUFFIX_RANDOM_INT = f'''
                random_int={VAR_NAME_RANDOM_INT},'''
'''
PEP-compliant code snippet passing the value of the random integer previously
generated for the current call to the exception-handling function call embedded
in the :data:`PEP_CODE_HINT_ROOT_SUFFIX` snippet.
'''

# ....................{ HINT ~ pep : (484|585) : generic  }....................
PEP484585_CODE_HINT_GENERIC_PREFIX = '''(
{indent_curr}    # True only if this pith is of this generic type.
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each unerased pseudo-superclass subclassed by a :pep:`484`-compliant
**generic** (i.e., PEP-compliant type hint subclassing a combination of one or
more of the :mod:`typing.Generic` superclass, the :mod:`typing.Protocol`
superclass, and/or other :mod:`typing` non-class objects).

Caveats
----------
The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


PEP484585_CODE_HINT_GENERIC_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each unerased pseudo-superclass subclassed by a :pep:`484`-compliant
generic.
'''


PEP484585_CODE_HINT_GENERIC_CHILD = '''
{{indent_curr}}    # True only if this pith deeply satisfies this unerased
{{indent_curr}}    # pseudo-superclass of this generic.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet type-checking the current pith against the current
unerased pseudo-superclass subclassed by a :pep:`484`-compliant generic.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last unerased pseudo-superclass of such a generic.
While there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''

# ....................{ HINT ~ pep : (484|585) : sequence }....................
PEP484585_CODE_HINT_SEQUENCE_ARGS_1 = '''(
{indent_curr}    # True only if this pith is of this sequence type.
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this pith is empty *OR* this pith is
{indent_curr}    # both non-empty and a random item deeply satisfies this hint.
{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
{indent_curr})'''
'''
PEP-compliant code snippet type-checking the current pith against a parent
**standard sequence type** (i.e., PEP-compliant type hint accepting exactly one
subscripted type hint unconditionally constraining *all* items of this pith,
which necessarily satisfies the :class:`collections.abc.Sequence` protocol with
guaranteed ``O(1)`` indexation across all sequence items).

Caveats
----------
**This snippet cannot contain ternary conditionals.** For unknown reasons
suggesting a critical defect in the current implementation of Python 3.8's
assignment expressions, this snippet raises :class:`UnboundLocalError`
exceptions resembling the following when this snippet contains one or more
ternary conditionals:

    UnboundLocalError: local variable '__beartype_pith_1' referenced before assignment

In particular, the initial draft of this snippet guarded against empty
sequences with a seemingly reasonable ternary conditional:

.. code-block:: python

   PEP484585_CODE_HINT_SEQUENCE_ARGS_1 = \'\'\'(
   {indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
   {indent_curr}    {hint_child_placeholder} if {pith_curr_var_name} else True
   {indent_curr})\'\'\'

That should behave as expected, but doesn't, presumably due to obscure scoping
rules and a non-intuitive implementation of ternary conditionals in CPython.
Ergo, the current version of this snippet guards against empty sequences with
disjunctions and conjunctions (i.e., ``or`` and ``and`` operators) instead.
Happily, the current version is more efficient than the equivalent approach
based on ternary conditional (albeit slightly less intuitive).
'''


PEP484585_CODE_HINT_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
    f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')
'''
PEP-compliant Python expression yielding the value of a randomly indexed item
of the current pith (which, by definition, *must* be a standard sequence).
'''

# ....................{ HINT ~ pep : (484|585) : tuple    }....................
PEP484585_CODE_HINT_TUPLE_FIXED_PREFIX = '''(
{indent_curr}    # True only if this pith is a tuple.
{indent_curr}    isinstance({pith_curr_assign_expr}, tuple) and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each subscripted child hint of an itemized :class:`typing.Tuple` type
of the form ``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each subscripted child hint of an itemized :class:`typing.Tuple` type
of the form ``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_EMPTY = '''
{{indent_curr}}    # True only if this tuple is empty.
{{indent_curr}}    not {pith_curr_var_name} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
to be empty against an itemized :class:`typing.Tuple` type of the non-standard
form ``typing.Tuple[()]``.

See Also
----------
:data:`PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_LEN = '''
{{indent_curr}}    # True only if this tuple is of the expected length.
{{indent_curr}}    len({pith_curr_var_name}) == {hint_childs_len} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
to be of the expected length against an itemized :class:`typing.Tuple` type of
the non-standard form ``typing.Tuple[()]``.

See Also
----------
:data:`PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD`
    Further details.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_CHILD = '''
{{indent_curr}}    # True only if this item of this non-empty tuple deeply
{{indent_curr}}    # satisfies this child hint.
{{indent_curr}}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet type-checking the current pith against the current
child hint subscripting an itemized :class:`typing.Tuple` type of the form
``typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]``.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted child hint of an itemized
:class:`typing.Tuple` type. While there exist alternate and more readable means
of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent type has been generated.
'''


PEP484585_CODE_HINT_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR = (
    '''{pith_curr_var_name}[{pith_child_index}]''')
'''
PEP-compliant Python expression yielding the value of the currently indexed
item of the current pith (which, by definition, *must* be a tuple).
'''

# ....................{ HINT ~ pep : (484|585) : subclass }....................
PEP484585_CODE_HINT_SUBCLASS = '''(
{indent_curr}    # True only if this pith is a class *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, type) and
{indent_curr}    # True only if this class subclasses this superclass.
{indent_curr}    issubclass({pith_curr_var_name}, {hint_curr_expr})
{indent_curr})'''
'''
PEP-compliant code snippet type-checking the current pith to be a subclass of
the subscripted child hint of a :pep:`484`- or :pep:`585`-compliant **subclass
type hint** (e.g., :attr:`typing.Type`, :class:`type`).
'''

# ....................{ HINT ~ pep : 484 : instance       }....................
PEP484_CODE_HINT_INSTANCE = (
    '''isinstance({pith_curr_expr}, {hint_curr_expr})''')
'''
PEP-compliant code snippet type-checking the current pith against the
current child PEP-compliant type expected to be a trivial non-:mod:`typing`
type (e.g., :class:`int`, :class:`str`).
'''

# ....................{ HINT ~ pep : 484 : union          }....................
PEP484_CODE_HINT_UNION_PREFIX = '''('''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against each subscripted argument of a :class:`typing.Union` type hint.
'''


PEP484_CODE_HINT_UNION_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each subscripted argument of a :class:`typing.Union` type hint.
'''


PEP484_CODE_HINT_UNION_CHILD_PEP = '''
{{indent_curr}}    {hint_child_placeholder} or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
PEP-compliant child argument subscripting a parent :class:`typing.Union` type
hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" or"`` after
applying this snippet to the last subscripted argument of such a hint. While
there exist alternate and more readable means of accomplishing this, this
approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''


PEP484_CODE_HINT_UNION_CHILD_NONPEP = '''
{{indent_curr}}    # True only if this pith is of one of these types.
{{indent_curr}}    isinstance({pith_curr_expr}, {hint_curr_expr}) or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
PEP-noncompliant child argument subscripting a parent :class:`typing.Union`
type hint.

See Also
----------
:data:`PEP484_CODE_HINT_UNION_CHILD_PEP`
    Further details.
'''

# ....................{ HINT ~ pep : 586                  }....................
PEP586_CODE_HINT_PREFIX = '''(
{{indent_curr}}    # True only if this pith is of one of these literal types.
{{indent_curr}}    isinstance({pith_curr_assign_expr}, {hint_child_types_expr}) and ('''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against a :pep:`586`-compliant :class:`typing.Literal` type hint subscripted by
one or more literal objects.
'''


PEP586_CODE_HINT_SUFFIX = '''
{indent_curr}))'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against a :pep:`586`-compliant :class:`typing.Literal` type hint subscripted by
one or more literal objects.
'''


PEP586_CODE_HINT_LITERAL = '''
{{indent_curr}}        # True only if this pith is equal to this literal.
{{indent_curr}}        {pith_curr_var_name} == {hint_child_expr} or'''
'''
PEP-compliant code snippet type-checking the current pith against the current
child literal object subscripting a :pep:`586`-compliant
:class:`typing.Literal` type hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Literal` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.

The ``{indent_curr}`` format variable is intentionally brace-protected to
efficiently defer its interpolation until the complete PEP-compliant code
snippet type-checking the current pith against *all* subscripted arguments of
this parent hint has been generated.
'''

# ....................{ HINT ~ pep : 593                  }....................
PEP593_CODE_HINT_VALIDATOR_PREFIX = '''(
{indent_curr}    {hint_child_placeholder} and'''
'''
PEP-compliant code snippet prefixing all code type-checking the current pith
against a :pep:`593`-compliant :class:`typing.Annotated` type hint subscripted
by one or more :class:`beartype.vale._SubscriptedIs` objects.
'''


PEP593_CODE_HINT_VALIDATOR_SUFFIX = '''
{indent_curr})'''
'''
PEP-compliant code snippet suffixing all code type-checking the current pith
against each a :pep:`593`-compliant :class:`typing.Annotated` type hint
subscripted by one or more :class:`beartype.vale._SubscriptedIs` objects.
'''


PEP593_CODE_HINT_VALIDATOR_CHILD = '''
{indent_curr}    # True only if this pith satisfies this caller-defined
{indent_curr}    # validator of this annotated.
{indent_curr}    {hint_child_expr} and'''
'''
PEP-compliant code snippet type-checking the current pith against
:mod:`beartype`-specific **data validator code** (i.e., caller-defined
:meth:`beartype.vale._SubscriptedIs._is_valid_code` string) of the current
child :class:`beartype.vale._SubscriptedIs` argument subscripting a parent `PEP
593`_-compliant :class:`typing.Annotated` type hint.

Caveats
----------
The caller is required to manually slice the trailing suffix ``" and"`` after
applying this snippet to the last subscripted argument of such a
:class:`typing.Annotated` type. While there exist alternate and more readable
means of accomplishing this, this approach is the optimally efficient.
'''

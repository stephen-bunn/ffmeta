# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains validators useful for tag definitions in the types module."""

import re
from datetime import datetime
from functools import partial
from typing import Any, Callable, Set

import wrapt


@wrapt.decorator
def validator(wrapped, _, args: list, kwargs: dict) -> Callable[[str], Any]:
    """Decorate validator callables so they return ready partials."""

    return partial(wrapped, *args, **kwargs)


@validator
def validate_pattern(pattern: str, value: str):
    """Validate that a value matches a given pattern.

    Args:
        pattern (str):
            The regex pattern the value should match
        value (str):
            The value to validate

    Raises:
        ValueError:
            If the given value does not match the given pattern
    """

    if re.match(pattern, value):
        return

    raise ValueError(f"{value!r} does not match pattern {pattern!r}")


@validator
def validate_choice(choices: Set[str], value: str):
    """Validate that a value matches one of the given choices.

    Args:
        choices (Set[str]):
            A set of strings that the value must match
        value (str):
            The value to validate

    Raises:
        ValueError:
            If the given value is not one of the given choices
    """

    if value in choices:
        return

    raise ValueError(f"{value!r} is not a valid choice, available are {choices!r}")


@validator
def validate_dateformat(format: str, value: str):
    """Validate that a value matches the given date format.

    Args:
        format (str):
            The date format the value must match
        value (str):
            The value to validate

    Raises:
        ValueError:
            If the given value does not match the given date format
    """

    try:
        datetime.strptime(value, format)
    except ValueError:
        raise ValueError(f"{value!r} does not match date format {format!r}")


@validator
def validate_max_length(max_length: int, value: str):
    """Validate that a value is not larger than a given length.

    Args:
        max_length (int):
            The maximum amount of characters the value can be
        value (str):
            The value to validate

    Raises:
        ValueError:
            If the given value is larger than the given maximum
    """

    if len(value) > max_length:
        raise ValueError(f"{value!r} is longer than {max_length!s} characters")

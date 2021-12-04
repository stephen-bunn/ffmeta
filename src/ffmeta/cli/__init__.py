# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Bootstraps the main CLI app."""

from .app import app

__all__ = ["app"]

if __name__ == "__main__":
    app()

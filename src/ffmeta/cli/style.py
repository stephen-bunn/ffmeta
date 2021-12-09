# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains UI presentation styles."""

from rich.style import Style

debug_style = Style(dim=True)
info_style = Style(color="cyan", bold=True)
accent_style = Style(color="magenta", bold=True)
danger_style = Style(color="red")
critical_style = Style(color="red", bold=True)
success_style = Style(color="green", bold=True)

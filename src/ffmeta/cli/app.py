# -*- encoding: utf-8 -*-
# Copyright (c) 2021 st37 <st37@tuta.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the main CLI app."""

import warnings
from pathlib import Path
from typing import Optional

import typer

from ffmeta.cli.ui import (
    build_chapters_renderable,
    build_header_renderable,
    build_tags_renderable,
)
from ffmeta.serialize import dumps_metadata, load_metadata
from ffmeta.services import probe_metadata

from .edit import edit_app
from .helpers import apply_metadata
from .utils import ensure_path_exists, get_console

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
app.add_typer(edit_app)


@app.callback()
def main(
    ctx: typer.Context,
    color: bool = typer.Option(default=True, help="Enable color output."),
    warn: bool = typer.Option(default=False, help="Enable warnings output."),
):
    """FFMeta.

    FFMpeg-based media metadata utility.
    """

    if not warn:
        warnings.simplefilter("ignore")


@app.command("probe")
def probe(ctx: typer.Context, media: Path = typer.Argument(...)):
    """Probe some media file for existing metadata."""

    console = get_console(ctx)
    ensure_path_exists(console, media)

    console.print_json(dumps_metadata(probe_metadata(media)))


@app.command("apply")
def apply(
    ctx: typer.Context,
    media: Path = typer.Argument(...),
    metadata: Path = typer.Argument(...),
    out: Optional[Path] = typer.Option(None, "-o", "--out"),
    overwrite: bool = typer.Option(False),
):
    """Apply some existing probed metadata to some media."""

    console = get_console(ctx)
    ensure_path_exists(console, media)
    ensure_path_exists(console, metadata)

    with metadata.open("r") as metadata_io:
        meta = load_metadata(metadata_io)

    apply_metadata(console, media, meta, output_filepath=out, overwrite=overwrite)


@app.command("show")
def show(ctx: typer.Context, media: Path = typer.Argument(...)):
    """Show some media metadata."""

    console = get_console(ctx)
    ensure_path_exists(console, media)

    metadata = probe_metadata(media)
    console.clear()
    console.print(build_header_renderable("Metadata", media))
    console.print(build_tags_renderable(metadata.iter_defined_tags(), title="Tags"))
    console.print(build_chapters_renderable(metadata.chapters, title="Chapters"))

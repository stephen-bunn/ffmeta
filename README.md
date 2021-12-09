# ffmeta

> A basic tool to write media metadata using ffmpeg.

**Use at your own risk.**

This is a personal tool.

- It is untested
- It is poorly documented
- It will definitely not work as expected
- It is not user-friendly
- It was mostly a waste of time to write

Furthermore, note that I keep using the term "media".
Realistically, I only have the intention of "media" referring to videos.
Audio and especially images will likely not work at all.

---

## Usage

If you do make the mistake of using this, here is an outline of avaialble commands.

### Probe Metadata

```console
$ ffmeta probe {MEDIA_FILEPATH}
... json content ...
```

Basically, this just runs `ffprobe`, loads the data into new types and dumps the JSON-serialized types out to STDOUT.

### Apply Metadata

```console
$ ffmeta apply {MEDIA_FILEPATH} {METADATA_FILEPATH}
...
```

This will apply the JSON-serialized types from `ffmeta probe` (written out to a file) and apply them to the given media file using `ffmpeg`.

### Show Metadata

```console
$ ffmeta show {MEDIA_FILEPATH}
```

This will display metadata (tags and chapters) from some media in CLI tables.


## Edit Usage

The primary reason I wanted this tool was to allow easy editing of media tags and chapters using ffmpeg.
It can be annoying to deal with ffmpeg's strange exchange format that looks like `.ini` but doesn't follow the spec exactly.

More importantly, I wanted desired metadata tags to be _required_ when adding / editing tags.
The `edit` subcommand will assist with editing information already present in some media.

### Edit Tags

```console
$ ffmeta edit tags {MEDIA_FILEPATH}
... prompts user for editing tags ...
```

This will prompt the user to fill out required and any desired tags for the media.
After the prompt is finished, the new tags will be written out to a new media file with metadata reencoded.

### Edit Chapters

```console
$ ffmeta edit chapters {MEDIA_FILEPATH}
... prompts user for editing chapters ...
```

This will prompt the user to fill out chapter information for the media.
After the prompt is finished, the new chapters will be written out to a new media file with metadata reencoded.

### Edit All

```console
$ ffmeta edit all {MEDIA_FILEPATH}
... prompts user to edit tags and chapters ...
```

This operates the same as the edit tags and chapters commands being run one after the other.
Media with the new data will only be reencoded once; so after editing tags the user will be immediatly prompted to edit chapters as well.


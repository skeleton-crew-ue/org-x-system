import re
from pathlib import Path

import pandas as pd
from dateutil import parser as dateparser

LINE_RE = re.compile(r"^\[(.+?)\] ([^:]+): (.*)$")


def _iter_text_lines(file_obj):
    if isinstance(file_obj, (str, Path)):
        with open(file_obj, encoding="utf-8") as f:
            yield from f
        return
    for line in file_obj:
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        yield line


def parse_export(file_obj):
    """Parse a WhatsApp chat export into a DataFrame.

    Accepts a path (str/Path) or an already-open file-like object, in
    either text mode (e.g. plain `open()`) or binary mode (e.g. Django's
    `FieldFile.open("rb")`).
    """
    messages = []
    current = None
    for line in _iter_text_lines(file_obj):
        m = LINE_RE.match(line)
        if m:
            if current:
                messages.append(current)
            ts, sender, body = m.groups()
            current = {
                "timestamp": dateparser.parse(ts, fuzzy=True),
                "sender": sender.strip(),
                "body": body.rstrip("\n"),
            }
        elif current:
            current["body"] += "\n" + line.rstrip("\n")
    if current:
        messages.append(current)

    df = pd.DataFrame(messages)
    df["is_media"] = df["body"].str.contains("<Media omitted>", na=False)
    df["is_system"] = df["sender"] == "System"
    return df

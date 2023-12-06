#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

HTML = Path("templates/main.html").read_text()
POST = Path("templates/post.html").read_text()

ATOM = Path("templates/main.atom").read_text()
ATOM_POST = Path("templates/post.atom").read_text()


class Template:
    def __init__(self, template: str):
        self.template = template

    def _parse(self, text: str) -> tuple:
        parts = []
        i = 0
        length = len(text)

        start = 0
        end = 0
        while i < length:
            if text[i] == "{" and text[i + 1] == "{":
                parts.append(("text", text[start:end]))
                start = i + 2

                i = start
                while text[i] != "}" or text[i + 1] != "}":
                    i += 1
                end = i

                parts.append(("key", text[start:end]))

                start = i + 2
                end = start
                i = start
            else:
                i += 1
                end += 1

        parts.append(("text", text[start:end]))

        return parts

    def apply_part(self, part: str, variables: dict) -> str:
        (kind, item) = part
        if kind == "text":
            return item
        elif kind == "key":
            key, *functions = [x.strip() for x in item.split("|")]
            value = variables[key]
            for function in functions:
                value = variables[function](value)
            return str(value)
        else:
            exit("Expected \"text\" or \"key\", got " + repr(kind))

    def apply(self, variables: dict) -> str:
        parts = self._parse(self.template)
        return "".join([self.apply_part(part, variables) for part in parts])


# FIXME: Once Netlify supports Py3.9+, change {**a, **b} and similar to a | b.

def parse_datetime(dt):
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

functions = {
    "join-lines": lambda l: "\n".join(l),
    "friendly-datetime": lambda dt: parse_datetime(dt).strftime("%b %d, %Y %I:%M%p"),
    "postify-each": lambda l: [Template(POST).apply({**post, **functions}) for post in l],
    "datetime-to-slug": lambda dt: parse_datetime(dt).strftime("%Y-%m-%d-%I:%M%p"),
    "atom-tag": lambda dt: parse_datetime(dt).strftime("tag:duckinator.net,%Y-%m-%d:%H%M"),
    "atom-datetime": lambda dt: parse_datetime(dt).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "atomize-each":  lambda l: [Template(ATOM_POST).apply({**post, **functions}) for post in l],
    "dict-get-dt": lambda d: d["datetime"],
    "first": lambda l: l[0],
    "last": lambda l: l[-1],
    "lines": lambda s: s.split("\n"),
}

posts = [{"datetime": p.stem.replace(".", ":").replace("_", " "), "text": p.read_text()} for p in Path("posts").glob("*.html")]
posts = sorted(posts, key=lambda x: x["datetime"], reverse=True)

site = Path("_site")
site.mkdir(exist_ok=True)

html = Template(HTML).apply({"posts": posts, **functions})
(site / "index.html").write_text(html)
atom = Template(ATOM).apply({"posts": posts, **functions})
(site / "atom.xml").write_text(atom)

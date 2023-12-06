#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

HTML = """\
<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { background: #fafaff; }
main {
    font-family: helvetica, sans-serif;
    font-size: 1.3rem;
    max-width: 60ch;
    margin: 0 auto;
}
section {
    border: 1px solid #000;
    border-radius: 0.25em;
}
h1 { font-size: 2rem; }
p, time { margin: 1em; }
time {
    font-size: 0.8em;
    display: block;
    text-align: right;
}
ul {
    list-style: none;
    margin: 0;
    padding: 0;
}
a, a:visited { color: #166491; }
a:active, a:focus, a:hover{ color: #2197db; }
</style>
<main>
<h1>Recent Updates for @duckinator</h1>

{{ posts | postify-each | join-lines }}
</main>
"""

POST = """\
<section id="{{ datetime | datetime-to-slug }}">
<p>{{ text }}</p>
<a href="#{{ datetime | datetime-to-slug }}">
    <time datetime="{{ datetime }}">{{ datetime | friendly-datetime }}</time>
</a>
</section>
"""

ATOM = """\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>@duckinator updates</title>
  <link href="http://news.do1g.com/"/>
  <updated>{{ posts | first | dict-get-dt | atom-datetime }}</updated>
  <author>
    <name>Ellen Marie Dash</name>
  </author>
  <id>https://news.do1g.com/</id>

  {{ posts | atomize-each | join-lines }}
</feed>
"""

ATOM_POST = """\

    <entry>
        <title>{{ text }}</title>
        <link href="https://news.do1g.com/#{{ datetime | datetime-to-slug }}" />
        <id>{{ datetime | atom-tag }}</id>
        <updated>{{ datetime | atom-datetime }}</updated>
        <content>
    </entry>
"""


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
}

posts = [{"datetime": p.stem.replace(".", ":").replace("_", " "), "text": p.read_text()} for p in Path("posts").glob("*.txt")]
posts = sorted(posts, key=lambda x: x["datetime"], reverse=True)

site = Path("_site")
site.mkdir(exist_ok=True)

html = Template(HTML).apply({"posts": posts, **functions})
(site / "index.html").write_text(html)
atom = Template(ATOM).apply({"posts": posts, **functions})
(site / "atom.xml").write_text(atom)

"""Builds assets/terminal.svg: a fake terminal window with an ASCII portrait
(assets/portrait.txt) on the left and `cat about.json` on the right.

Edit ABOUT below, run `python generate.py`, commit the regenerated SVG.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent

# ----------------------------------------------------------------- content
ABOUT = {
    "name": "Tomáš Greguš",
    "role": "Full-stack Web Developer",
    "study": "Software Engineering @ UTB Zlín",
    "location": "Czech Republic",
    "uptime": "20 years, 4 months, 1 day",
    "stack": {
        "languages": ["TypeScript", "JavaScript", "PHP", "C#"],
        "frontend": ["React", "Next.js", "Astro", "Tailwind"],
        "backend": ["Firebase", "Supabase", "MySQL"],
        "tools": ["Git", "Vercel", "Figma"],
    },
    "focus": ["web apps", "SEO", "performance"],
    "highlights": [
        "PrimePay: award-winning hackathon app",
        "jsemzvosku.cz: Lighthouse 92/100/100/100",
        "3DTiskDesign: top 10 on Google",
    ],
    "github": {
        "repos": 11,
        "contributions_1y": 1031,
        "top_language": "TypeScript (89.5%)",
    },
    "contact": {
        "email": "gregustomas@seznam.cz",
        "web": "tomasgregus.cz",
        "linkedin": "in/tomas-gregus",
    },
}

USER, HOST, PATH = "tomas", "github", "~"
TITLE = f"{USER}@{HOST}: {PATH}"

# ------------------------------------------------------------------ theme
C = {
    "bg": "#0d1117",
    "bar": "#161b22",
    "border": "#30363d",
    "ascii": "#d0d7de",
    "punct": "#8b949e",
    "key": "#79c0ff",
    "str": "#a5d6ff",
    "num": "#ffa657",
    "user": "#d2a8ff",
    "path": "#7ee787",
    "cmd": "#e6edf3",
    "title": "#8b949e",
}
FONT = "ui-monospace, SFMono-Regular, 'Cascadia Code', Menlo, Consolas, 'Liberation Mono', monospace"

# ----------------------------------------------------------------- layout
W, H = 1200, 745
BAR_H = 42
ASCII_X, ASCII_Y = 30, BAR_H + 24
ASCII_FS, ASCII_CW, ASCII_LH = 8.7, 5.2, 10.4     # font-size, char width, line height
JSON_X, JSON_FS, JSON_CW, JSON_LH = 620, 13.5, 8.1, 16.6
PROMPT_Y = BAR_H + 30


# -------------------------------------------------------- json -> tokens
def render(value, indent=0):
    """Return list of lines; each line is a list of (class, text) tokens."""
    pad = "  " * indent
    if isinstance(value, dict):
        width = max(len(k) for k in value)
        lines = []
        items = list(value.items())
        for i, (k, v) in enumerate(items):
            comma = [("punct", ",")] if i < len(items) - 1 else []
            key = [("punct", pad + "  "), ("key", f'"{k}"'), ("punct", ":")]
            if isinstance(v, dict):
                sub = render(v, indent + 1)
                lines.append(key + [("punct", " {")])
                lines.extend(sub[1:-1])
                lines.append([("punct", pad + "  }")] + comma)
            elif isinstance(v, list) and len(", ".join(map(str, v))) > 44:
                lines.append(key + [("punct", " [")])
                for j, x in enumerate(v):
                    c2 = [("punct", ",")] if j < len(v) - 1 else []
                    lines.append([("punct", pad + "    "), scalar(x)] + c2)
                lines.append([("punct", pad + "  ]")] + comma)
            else:
                gap = " " * (width - len(k) + 1)
                lines.append(key + [("punct", gap)] + inline(v) + comma)
        return [[("punct", pad + "{")]] + lines + [[("punct", pad + "}")]]
    raise TypeError(value)


def scalar(x):
    if isinstance(x, bool):
        return ("num", str(x).lower())
    if isinstance(x, (int, float)):
        return ("num", str(x))
    return ("str", '"' + str(x) + '"')


def inline(v):
    if isinstance(v, list):
        out = [("punct", "[")]
        for i, x in enumerate(v):
            out.append(scalar(x))
            if i < len(v) - 1:
                out.append(("punct", ", "))
        out.append(("punct", "]"))
        return out
    return [scalar(v)]


# ---------------------------------------------------------------- svg out
def build():
    portrait = (ROOT / "assets" / "portrait.txt").read_text(encoding="utf-8").split("\n")
    cols = max(len(l) for l in portrait)
    out = []
    a = out.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Terminal: ASCII portrait of Tomáš Greguš and his about.json">')
    a("<style>"
      f"text{{font-family:{FONT};white-space:pre}}"
      ".k{fill:%(key)s}.s{fill:%(str)s}.n{fill:%(num)s}.p{fill:%(punct)s}"
      "@keyframes blink{0%%,49%%{opacity:1}50%%,100%%{opacity:0}}"
      ".cur{animation:blink 1.1s steps(1) infinite}"
      "</style>" % C)

    # window
    a(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{C["bg"]}" stroke="{C["border"]}"/>')
    a(f'<path d="M1 {BAR_H} V15 a14 14 0 0 1 14 -14 H{W-15} a14 14 0 0 1 14 14 V{BAR_H} Z" fill="{C["bar"]}"/>')
    a(f'<line x1="1" x2="{W-1}" y1="{BAR_H}" y2="{BAR_H}" stroke="{C["border"]}"/>')
    for i, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        a(f'<circle cx="{26 + i*20}" cy="{BAR_H/2}" r="6" fill="{col}"/>')
    a(f'<text x="{W/2}" y="{BAR_H/2+4.5}" font-size="13" text-anchor="middle" fill="{C["title"]}">{escape(TITLE)}</text>')

    # ascii portrait (textLength pins the width regardless of the viewer's mono font)
    for i, line in enumerate(portrait):
        y = ASCII_Y + i * ASCII_LH
        a(f'<text x="{ASCII_X}" y="{y:.1f}" font-size="{ASCII_FS}" fill="{C["ascii"]}" '
          f'textLength="{cols*ASCII_CW:.1f}" lengthAdjust="spacing" xml:space="preserve">{escape(line.ljust(cols))}</text>')

    # prompt + json
    prompt = (f'<tspan fill="{C["user"]}">{USER}</tspan><tspan fill="{C["cmd"]}">@</tspan>'
              f'<tspan fill="{C["user"]}">{HOST}</tspan><tspan fill="{C["cmd"]}">:</tspan>'
              f'<tspan fill="{C["path"]}">{escape(PATH)}</tspan><tspan fill="{C["cmd"]}">$ </tspan>')
    a(f'<text x="{JSON_X}" y="{PROMPT_Y}" font-size="{JSON_FS}" xml:space="preserve">{prompt}'
      f'<tspan fill="{C["cmd"]}">cat about.json</tspan></text>')

    cls = {"key": "k", "str": "s", "num": "n", "punct": "p"}
    lines = render(ABOUT)
    y = PROMPT_Y + JSON_LH + 4
    for toks in lines:
        spans = "".join(f'<tspan class="{cls[c]}">{escape(t)}</tspan>' for c, t in toks)
        a(f'<text x="{JSON_X}" y="{y:.1f}" font-size="{JSON_FS}" xml:space="preserve">{spans}</text>')
        y += JSON_LH
    y += 4
    a(f'<text x="{JSON_X}" y="{y:.1f}" font-size="{JSON_FS}" xml:space="preserve">{prompt}</text>')
    prompt_len = len(f"{USER}@{HOST}:{PATH}$ ")
    a(f'<rect class="cur" x="{JSON_X + prompt_len*JSON_CW:.1f}" y="{y-JSON_FS+2:.1f}" width="{JSON_CW:.1f}" '
      f'height="{JSON_FS+1}" fill="{C["cmd"]}"/>')

    a("</svg>")
    return "\n".join(out), y


if __name__ == "__main__":
    svg, last_y = build()
    (ROOT / "assets" / "terminal.svg").write_text(svg, encoding="utf-8")
    print(f"assets/terminal.svg written ({len(svg)//1024} KiB); last json y={last_y:.0f} of {H}")

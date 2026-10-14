"""Draws the eight fish illustrations (facing left). SVG sources go to tools/fish-svg/, transparent PNGs to web/fish/.
Run:  pip install cairosvg && python tools/make_fish_art.py        Edit the SPECS below to change colours or proportions.
The PNGs are placeholders: replace web/fish/<id>.png with a real transparent photo of the same name any time."""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "web" / "fish"
SVG_OUT = Path(__file__).resolve().parent / "fish-svg"
PNG_SIZE = (1260, 600)                    # 3x of the 420 x 200 drawing: sharp on phones
X0, X1, CY = 30.0, 318.0, 100.0          # nose, end of the tail stalk, centre line
L = X1 - X0


def half(t, H, tm, p, q, r):
    """Half the body height at position t (0 nose .. 1 tail stalk)."""
    g = (t / tm) ** p if t < tm else r + (1 - r) * ((1 - t) / (1 - tm)) ** q
    return H * g


class Fish:
    def __init__(self, s):
        self.s = s

    def top(self, t):
        s = self.s
        bump = s.get("fore", 0) * s["H"] * math.exp(-((t - 0.09) / 0.085) ** 2)
        return half(t, s["H"], s["tm"], s["p"], s["q"], s["r"]) * s.get("topf", 1.0) + bump

    def bot(self, t):
        s = self.s
        return half(t, s["H"], s["tm"], s["p"], s["q"], s["r"]) * s.get("botf", 1.0)

    def x(self, t):
        return X0 + L * t

    def pt_top(self, t):
        return (self.x(t), CY - self.top(t))

    def pt_bot(self, t):
        return (self.x(t), CY + self.bot(t))


def f(v):
    return f"{v:.1f}"


def pathpts(pts):
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def body_path(fi, n=90):
    top = [fi.pt_top(i / n) for i in range(n + 1)]
    bot = [fi.pt_bot(i / n) for i in range(n, -1, -1)]
    return pathpts(top + bot)


def dorsal(fi, t1, t2, h, tp, color, rake=0.0, op=1.0):
    (x1, y1), (x2, y2) = fi.pt_top(t1), fi.pt_top(t2)
    xp, yp = fi.x(tp), fi.pt_top(tp)[1] - h
    w = x2 - x1
    d = (f"M{f(x1)},{f(y1 + 2)} C{f(x1 + w * 0.05)},{f(yp + h * 0.55)} {f(xp - w * (0.12 + rake))},{f(yp)} {f(xp)},{f(yp)} "
         f"C{f(xp + w * 0.30)},{f(yp + h * 0.12)} {f(x2 - w * 0.02)},{f(y2 - h * 0.45)} {f(x2)},{f(y2 + 2)} Z")
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def anal(fi, t1, t2, h, color, op=1.0):
    (x1, y1), (x2, y2) = fi.pt_bot(t1), fi.pt_bot(t2)
    d = (f"M{f(x1)},{f(y1 - 2)} C{f(x1 + 4)},{f(y1 + h * 0.8)} {f(x1 + (x2 - x1) * 0.25)},{f(y1 + h)} {f(x1 + (x2 - x1) * 0.45)},{f(y1 + h)} "
         f"C{f(x1 + (x2 - x1) * 0.7)},{f(y1 + h * 0.7)} {f(x2 - 3)},{f(y2 + h * 0.3)} {f(x2)},{f(y2 - 2)} Z")
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def finlets(fi, t1, t2, n, h, color, top=True):
    out = []
    for i in range(n):
        t = t1 + (t2 - t1) * i / max(1, n - 1)
        x, y = fi.pt_top(t) if top else fi.pt_bot(t)
        sgn = -1 if top else 1
        out.append(f'<path d="M{f(x)},{f(y)} L{f(x + 11)},{f(y + sgn * h)} L{f(x + 15)},{f(y)} Z" fill="{color}"/>')
    return "".join(out)


def tail(fi, color, S, L1, notch, upper=1.0, lower=1.0, op=1.0):
    ph = fi.top(1.0)
    pb = fi.bot(1.0)
    su, sl = S * upper, S * lower
    d = (f"M{f(X1 - 4)},{f(CY - ph)} Q{f(X1 + 30)},{f(CY - su * 0.75)} {f(X1 + L1 * upper)},{f(CY - su)} "
         f"Q{f(X1 + notch + 14)},{f(CY - su * 0.28)} {f(X1 + notch)},{f(CY)} "
         f"Q{f(X1 + notch + 14)},{f(CY + sl * 0.28)} {f(X1 + L1 * lower)},{f(CY + sl)} "
         f"Q{f(X1 + 30)},{f(CY + sl * 0.75)} {f(X1 - 4)},{f(CY + pb)} Z")
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def pectoral(fi, color, t=0.27, length=40, op=0.95):
    x, y = fi.x(t), CY + fi.bot(t) * 0.25
    d = f"M{f(x)},{f(y - 6)} Q{f(x + length * 0.55)},{f(y - 4)} {f(x + length)},{f(y + length * 0.55)} Q{f(x + length * 0.35)},{f(y + 10)} {f(x - 2)},{f(y + 6)} Z"
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def pelvic(fi, color, t=0.33, length=30, op=0.95):
    x, y = fi.pt_bot(t)
    d = f"M{f(x)},{f(y - 3)} L{f(x + length * 0.9)},{f(y + length)} L{f(x + length * 0.45)},{f(y - 1)} Z"
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def eye(fi, t=0.085, r=6.0, dy=0.2):
    x, y = fi.x(t), CY - fi.top(t + 0.02) * dy
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r + 1.6)}" fill="#ffffff" fill-opacity="0.9"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="#0b1220"/><circle cx="{f(x - r * 0.3)}" cy="{f(y - r * 0.35)}" r="{f(r * 0.28)}" fill="#ffffff"/>')


def gill(fi, t=0.215, color="#000000", op=0.28):
    (xt, yt), (xb, yb) = fi.pt_top(t), fi.pt_bot(t)
    return f'<path d="M{f(xt)},{f(yt + 3)} Q{f(xt - 14)},{f(CY)} {f(xb - 4)},{f(yb - 3)}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="2.4" stroke-linecap="round"/>'


def mouth(fi, length=11, dy=0.18, color="#00000066"):
    x = X0 + 0.5
    y = CY + fi.bot(0.04) * dy
    return f'<path d="M{f(x)},{f(y)} L{f(x + length)},{f(y + 1.5)}" stroke="#0b1220" stroke-opacity="0.55" stroke-width="1.8" stroke-linecap="round"/>'


def render(s):
    fi = Fish(s)
    c = s["colors"]
    bill = ""
    if s.get("bill"):
        b = s["bill"]
        bill = (f'<path d="M{f(X0 + 6)},{f(CY - 5)} L{f(X0 - b)},{f(CY - 1.6)} L{f(X0 + 6)},{f(CY + 5)} Z" fill="{c["bill"]}"/>')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 200" role="img" aria-label="{s["name"]}">',
             "<defs>",
             f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["back"]}"/><stop offset="0.5" stop-color="{c["mid"]}"/><stop offset="1" stop-color="{c["belly"]}"/></linearGradient>',
             f'<clipPath id="b"><path d="{body_path(fi)}"/></clipPath>',
             '<linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.38"/><stop offset="0.35" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.22"/></linearGradient>',
             "</defs>"]
    parts.append(bill)
    for fn in s.get("behind", []):          # fins drawn behind the body
        parts.append(fn(fi))
    parts.append(f'<path d="{body_path(fi)}" fill="url(#g)"/>')
    parts.append('<g clip-path="url(#b)">')
    for fn in s.get("marks", []):           # stripes, bars and spots
        parts.append(fn(fi))
    parts.append(f'<path d="{body_path(fi)}" fill="url(#sh)"/>')
    parts.append("</g>")
    parts.append(f'<path d="{body_path(fi)}" fill="none" stroke="#000" stroke-opacity="0.3" stroke-width="1.3" stroke-linejoin="round"/>')
    for fn in s.get("front", []):           # fins drawn over the body
        parts.append(fn(fi))
    parts += [gill(fi), mouth(fi, s.get("mouth", 11)), eye(fi, s.get("eye_t", 0.085), s.get("eye_r", 6.0), s.get("eye_dy", 0.2)), "</svg>"]
    return "".join(parts)


# ---- marks ----
def stripe(y_off, w, color, op=1.0, t1=0.1, t2=1.0, wave=0):
    return lambda fi: (f'<path d="M{f(fi.x(t1))},{f(CY + y_off)} Q{f(fi.x((t1 + t2) / 2))},{f(CY + y_off + wave)} {f(fi.x(t2) + 6)},{f(CY + y_off)}" '
                       f'fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{w}" stroke-linecap="butt"/>')


def bars(n, t1, t2, color, op=0.5, w=7, slant=8):
    def fn(fi):
        out = []
        for i in range(n):
            x = fi.x(t1 + (t2 - t1) * i / max(1, n - 1))
            out.append(f'<path d="M{f(x)},{f(CY - 60)} L{f(x - slant)},{f(CY + 60)}" stroke="{color}" stroke-opacity="{op}" stroke-width="{w}"/>')
        return "".join(out)
    return fn


def dots(seed, n, t1, t2, y1, y2, color, r=1.9, op=0.7):
    def fn(fi):
        import random
        rnd = random.Random(seed)
        return "".join(f'<circle cx="{f(fi.x(rnd.uniform(t1, t2)))}" cy="{f(CY + rnd.uniform(y1, y2))}" r="{f(r * rnd.uniform(0.6, 1.3))}" fill="{color}" fill-opacity="{op}"/>' for _ in range(n))
    return fn


def scales(color, op=0.16, t1=0.2, t2=0.95, r=9):
    def fn(fi):
        out = []
        for i, t in enumerate([t1 + (t2 - t1) * k / 16 for k in range(17)]):
            for j in range(-5, 6):
                y = CY + j * r * 0.9 + (r * 0.45 if i % 2 else 0)
                x = fi.x(t)
                if -fi.top(t) * 0.92 < y - CY < fi.bot(t) * 0.92:
                    out.append(f'<path d="M{f(x)},{f(y - r * 0.5)} Q{f(x + r * 0.55)},{f(y)} {f(x)},{f(y + r * 0.5)}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="1.1"/>')
        return "".join(out)
    return fn


def patch(t, y_off, rx, ry, color, op=0.9):
    return lambda fi: f'<ellipse cx="{f(fi.x(t))}" cy="{f(CY + y_off)}" rx="{rx}" ry="{ry}" fill="{color}" fill-opacity="{op}"/>'


SPECS = {
 "mahi-mahi": dict(name="Mahi-mahi", H=47, tm=0.26, p=0.62, q=0.85, r=0.20, fore=0.5, botf=0.93, mouth=9, eye_r=6.2,
   colors=dict(back="#168a8f", mid="#e0c64a", belly="#f3efc2"),
   behind=[lambda fi: tail(fi, "#d7c63a", 62, 76, 44), lambda fi: dorsal(fi, 0.12, 0.93, 26, 0.45, "#1d9a9b", rake=-0.1), lambda fi: anal(fi, 0.5, 0.93, 20, "#c9c34c")],
   marks=[stripe(-10, 30, "#2fb7c0", 0.35, 0.1, 1.0), dots(3, 26, 0.18, 0.9, -26, 10, "#0c3d52", 2.0, 0.55), dots(9, 12, 0.2, 0.9, -34, -16, "#5be0e6", 1.8, 0.65)],
   front=[lambda fi: pectoral(fi, "#e7d65a", 0.27, 34), lambda fi: pelvic(fi, "#dcd070", 0.33, 24)]),
 "sailfish": dict(name="Sailfish", H=27, tm=0.30, p=0.82, q=0.8, r=0.16, bill=64, mouth=0, eye_r=5.4, eye_t=0.07,
   colors=dict(back="#13307c", mid="#5b84c8", belly="#eef2f7", bill="#3f5f9c"),
   behind=[lambda fi: tail(fi, "#1b3f94", 52, 70, 36), lambda fi: dorsal(fi, 0.20, 0.80, 56, 0.36, "#2457c7", rake=-0.05, op=0.95), lambda fi: dorsal(fi, 0.80, 0.90, 14, 0.85, "#1b3f94"), lambda fi: anal(fi, 0.62, 0.90, 17, "#315fc4")],
   marks=[dots(5, 22, 0.15, 0.95, -22, 8, "#0a1f5c", 1.7, 0.35), stripe(-4, 14, "#8db4ee", 0.35, 0.12, 1.0)],
   front=[lambda fi: pectoral(fi, "#254aa8", 0.28, 36), lambda fi: f'<path d="M{f(fi.x(0.31))},{f(CY + fi.bot(0.31) - 2)} Q{f(fi.x(0.38))},{f(CY + 62)} {f(fi.x(0.52))},{f(CY + 70)} Q{f(fi.x(0.40))},{f(CY + 40)} {f(fi.x(0.33))},{f(CY + fi.bot(0.31) - 2)} Z" fill="#2b55b8"/>']),
 "wahoo": dict(name="Wahoo", H=21, tm=0.34, p=0.96, q=0.9, r=0.17, bill=0, mouth=14, eye_r=4.6, eye_t=0.07,
   colors=dict(back="#1235a6", mid="#5f96d9", belly="#e8eef5"),
   behind=[lambda fi: tail(fi, "#1c3fa9", 48, 66, 38), lambda fi: dorsal(fi, 0.20, 0.82, 15, 0.38, "#2c52c4"), lambda fi: finlets(fi, 0.84, 0.97, 6, 9, "#3b63c9"), lambda fi: finlets(fi, 0.70, 0.97, 6, 9, "#9fb7dc", top=False)],
   marks=[bars(13, 0.18, 0.95, "#0e2a86", 0.55, 6.5, 10), stripe(2, 14, "#cfe0f5", 0.25, 0.12, 1.0)],
   front=[lambda fi: pectoral(fi, "#27479e", 0.26, 24)]),
 "yellowtail-snapper": dict(name="Yellowtail snapper", H=36, tm=0.40, p=0.78, q=0.7, r=0.17, mouth=9, eye_r=5.8,
   colors=dict(back="#6f86b3", mid="#c9cfd8", belly="#fbf6ee"),
   behind=[lambda fi: tail(fi, "#f6c91c", 56, 68, 34), lambda fi: dorsal(fi, 0.20, 0.84, 22, 0.5, "#f0cf3a", rake=0.02), lambda fi: anal(fi, 0.60, 0.88, 16, "#f3d860")],
   marks=[stripe(-3, 17, "#f5c518", 0.98, 0.04, 1.0, 5), dots(2, 40, 0.15, 0.85, -26, -9, "#e9a8a0", 1.8, 0.35)],
   front=[lambda fi: pectoral(fi, "#f1de72", 0.28, 30), lambda fi: pelvic(fi, "#f1de72", 0.34, 24)]),
 "mutton-snapper": dict(name="Mutton snapper", H=45, tm=0.40, p=0.75, q=0.7, r=0.19, mouth=9, eye_r=6.0,
   colors=dict(back="#7b6a3a", mid="#d98f6f", belly="#f6dfd2"),
   behind=[lambda fi: tail(fi, "#cf6f58", 56, 66, 32), lambda fi: dorsal(fi, 0.20, 0.86, 30, 0.34, "#c47a4f", rake=-0.12), lambda fi: anal(fi, 0.58, 0.88, 22, "#d98a6c")],
   marks=[dots(4, 34, 0.16, 0.9, -34, 4, "#7fc6e6", 1.7, 0.6), patch(0.77, -33, 7.5, 6.5, "#10161f", 0.9),
          lambda fi: f'<path d="M{f(fi.x(0.02))},{f(CY + 6)} Q{f(fi.x(0.07))},{f(CY + 9)} {f(fi.x(0.17))},{f(CY + 14)}" fill="none" stroke="#6ec2e8" stroke-width="2.4" stroke-linecap="round"/>'],
   front=[lambda fi: pectoral(fi, "#e39c80", 0.28, 32), lambda fi: pelvic(fi, "#e8a58b", 0.34, 26)]),
 "snook": dict(name="Common snook", H=29, tm=0.38, p=0.9, q=0.8, r=0.20, topf=0.95, botf=1.05, mouth=17, eye_r=5.6, eye_t=0.09, eye_dy=0.12,
   colors=dict(back="#6f7a42", mid="#c9cfa1", belly="#faf7e6"),
   behind=[lambda fi: tail(fi, "#bdb55a", 50, 60, 30), lambda fi: dorsal(fi, 0.34, 0.58, 18, 0.36, "#8e9254"), lambda fi: dorsal(fi, 0.66, 0.84, 17, 0.7, "#a3a362"), lambda fi: anal(fi, 0.66, 0.88, 14, "#c5bd63")],
   marks=[stripe(-3, 6.5, "#10130d", 0.92, 0.2, 1.0), scales("#4c5a2a", 0.12, 0.2, 0.95, 8)],
   front=[lambda fi: pectoral(fi, "#d9d27a", 0.27, 28), lambda fi: pelvic(fi, "#e2d97c", 0.34, 22)]),
 "tarpon": dict(name="Atlantic tarpon", H=51, tm=0.38, p=0.7, q=0.65, r=0.16, topf=0.92, botf=1.04, mouth=12, eye_r=8.0, eye_t=0.085, eye_dy=0.12,
   colors=dict(back="#3a5668", mid="#b9c6d0", belly="#f4f7fa"),
   behind=[lambda fi: tail(fi, "#44606f", 62, 74, 40), lambda fi: dorsal(fi, 0.50, 0.66, 28, 0.52, "#566f7f", rake=-0.2), lambda fi: f'<path d="M{f(fi.x(0.66))},{f(fi.pt_top(0.66)[1] - 26)} Q{f(fi.x(0.76))},{f(fi.pt_top(0.66)[1] - 40)} {f(fi.x(0.80))},{f(fi.pt_top(0.80)[1] - 4)}" fill="none" stroke="#566f7f" stroke-width="2"/>', lambda fi: anal(fi, 0.70, 0.88, 14, "#8a9ba6")],
   marks=[scales("#35505f", 0.30, 0.18, 0.97, 10), stripe(-20, 24, "#2b4658", 0.22, 0.1, 1.0)],
   front=[lambda fi: pectoral(fi, "#9db0bc", 0.28, 30), lambda fi: pelvic(fi, "#a7b6c0", 0.36, 24)]),
 "cobia": dict(name="Cobia", H=26, tm=0.34, p=0.85, q=0.85, r=0.17, topf=0.9, botf=1.0, mouth=15, eye_r=4.8, eye_t=0.075, eye_dy=0.15,
   colors=dict(back="#51402f", mid="#816a52", belly="#efe4d3"),
   behind=[lambda fi: tail(fi, "#33271c", 58, 82, 20, upper=1.0, lower=0.82), lambda fi: finlets(fi, 0.20, 0.38, 7, 11, "#2f241a"), lambda fi: dorsal(fi, 0.44, 0.92, 15, 0.50, "#3a2d21", rake=-0.1), lambda fi: anal(fi, 0.58, 0.92, 15, "#4a3a2a")],
   marks=[stripe(-1, 9, "#1a130d", 0.9, 0.16, 1.0), stripe(6, 4.5, "#c9b79b", 0.65, 0.2, 1.0)],
   front=[lambda fi: pectoral(fi, "#2f241a", 0.27, 30), lambda fi: pelvic(fi, "#3a2d21", 0.34, 20)]),
}

if __name__ == "__main__":
    import cairosvg
    OUT.mkdir(parents=True, exist_ok=True)
    SVG_OUT.mkdir(parents=True, exist_ok=True)
    for sid, spec in SPECS.items():
        svg = render(spec)
        (SVG_OUT / f"{sid}.svg").write_text(svg, encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(OUT / f"{sid}.png"), output_width=PNG_SIZE[0], output_height=PNG_SIZE[1])
        print("wrote", OUT / f"{sid}.png")

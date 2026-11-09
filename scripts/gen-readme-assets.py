#!/usr/bin/env python3
"""README visuals for dsh-aqua-input-check — derived from the plugin's real pipeline.

Two figures, both read off the shipped material rather than a generic template:

  hero 1440×576 (Pillow, 4 files)
      The material itself: a farm header plus rows of the input register. Row 1
      has both pond and species blank (AQ-001's finding); row 2 states a 30-day
      withdrawal period but is harvested on 06-20, 19 days after the 06-01 use
      date (AQ-004's arithmetic). Under the register sit the two outputs: the
      located finding card and the withdrawal-date arithmetic card, then the
      report line that keeps the verdict with the reviewer.

  flow 1100×660 (hand-written SVG, 2 files)
      A matrix, not a pipeline: seven rules (rows) × the register's field groups
      (columns). A filled dot means "this rule reads that column together";
      AQ-006 is hollow because its vocabulary ships empty, so the rule skips by
      default. Two output channels leave the matrix — `issues[]` (located by row
      and column) and `skipped[]` (with a reason) — and feed the reviewer.

Text values come from the repository's own fixtures, not from imagination:
  tests/fixtures/AQ-001/AQ-001-unsafe.json  (blank pondNo + species, 350 kg,
      2026-03-01, 0 d, harvest 2026-06-20)
  tests/fixtures/AQ-004/AQ-004-unsafe.json  (usedAt 2026-06-01, 30 d,
      harvest 2026-06-20 → 19 days, 11 days short)
  rules/aqua-input-check.yaml               (AQ-001..AQ-007, checks, severities)

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import math
import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

RADIUS = 22
SHADOW = 26

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        mark="#b45309", mark_bg="#fdf3e9",
        shadow=(32, 26, 64), glow2="#7a68c9",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        mark="#d9a441", mark_bg="#2a2216",
        shadow=(0, 0, 0), glow2="#8496f5",
    ),
}

FONT_FILES = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
              "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}


def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.15 * (y / h) + 0.85 * (y / h) ** 1.35
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: tuple, alpha: int = 40) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple, s: dict, radius: int = RADIUS,
         shadow: int = SHADOW, fill: str | None = None) -> Image.Image:
    """A soft-shadowed rounded card on the gradient background."""
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 5,
                             fill=s["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(s["card_edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    """Fail loudly instead of shipping a clipped label."""
    w = measure(text, size, kind)
    if w > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs {w:.1f}px > {max_w}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: {text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def wrap(d: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, maxw: float) -> list[str]:
    if " " in text:
        words, lines, cur = text.split(" "), [], ""
        for wd in words:
            cand = (cur + " " + wd) if cur else wd
            if d.textlength(cand, font=f) <= maxw or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) <= maxw or not cur:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> tuple[int, int]:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: int = 11, kind: str = "cjk_bold", padx: int = 9,
         height: int = 20) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + padx * 2, y + height],
                        radius=height // 2, fill=hx(bg))
    d.text((x + padx, y + height / 2), text, font=f, fill=hx(fg), anchor="lm")
    return int(w + padx * 2)


def dash_rect(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
              color: str, width: int = 2, dash: int = 7, gap: int = 5) -> None:
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)),
                 ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(dist // (dash + gap)) + 1
        for i in range(n):
            t0 = i * (dash + gap) / dist
            t1 = min((i * (dash + gap) + dash) / dist, 1.0)
            if t0 >= 1:
                break
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                   fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# Every value below is an excerpt of a fixture in this repository; see the
# module docstring for the mapping.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核查器",
        value=["七条规则，逐行逐栏核对", "差异落到行号与栏名"],
        sub=["只列材料内部能指认的差异：齐备性与日期算术；",
             "不判合规、不认定责任——结论留给审核人。"],
        meta="AQ-001..AQ-007 · 规则包即数据 · skipped 逐条说明",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="投入品记录 · rows[]",
        reg_chip="只读原件",
        farm="某某水产养殖场 · 某某镇某某村 · 86 亩 · 2026 年 2—6 月",
        headers=["塘口·品种", "投入品名称", "用量", "使用日期", "休药期", "起捕日期"],
        widths=[110, 178, 72, 96, 76, 96],
        rows=[
            ["—", "草鱼配合饲料 2 号", "350 kg", "2026-03-01", "0 天", "2026-06-20"],
            ["T-03 · 草鱼", "某某抗菌药", "350 kg", "2026-06-01", "30 天", "2026-06-20"],
            ["T-05 · 草鱼", "冰鲜鱼", "120 kg", "2026-05-12", "0 天", "2026-06-21"],
        ],
        note="列名忽略大小写、空格与下划线；原件永不修改",
        issue=dict(rule="AQ-001", sev="warn",
                   locator="第 1 行 · pondNo / species",
                   found="发现：pondNo、species 都为空",
                   expected="应填：至少填一项",
                   fix="建议：补填塘口编号与养殖品种"),
        arith=dict(rule="AQ-004", sev="warn",
                   formula="06-01 + 30 天 = 07-01",
                   harvest="起捕 06-20 · 只有 19 天",
                   bar_l="实 19 天", bar_r="应 ≥ 30 天",
                   note="少 11 天 · 只报算术，不判安全"),
        strip=("issues[] 2 条差异 · skipped[] 2 条未执行", "结论留给审核人"),
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Seven rules read every row", "each difference lands on a cell"],
        sub=["Completeness and withdrawal-date arithmetic —",
             "no compliance verdict; the reviewer decides."],
        meta="AQ-001..AQ-007 · rules are data · skipped always explained",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="Input register · rows[]",
        reg_chip="read-only",
        farm="Some Aquafarm · Some Village · 86 mu · Feb–Jun 2026",
        headers=["Pond · species", "Input name", "Qty", "Used on", "Withdrawal", "Harvest"],
        widths=[106, 172, 70, 94, 92, 94],
        rows=[
            ["—", "Grass-carp feed 2", "350 kg", "2026-03-01", "0 d", "2026-06-20"],
            ["T-03 · carp", "Antibacterial drug", "350 kg", "2026-06-01", "30 d", "2026-06-20"],
            ["T-05 · carp", "Chilled fish", "120 kg", "2026-05-12", "0 d", "2026-06-21"],
        ],
        note="Column names ignore case and spaces; the original is never modified",
        issue=dict(rule="AQ-001", sev="warn",
                   locator="Row 1 · pondNo / species",
                   found="Found: pondNo and species are blank",
                   expected="Expected: at least one filled",
                   fix="Fix: fill the pond number and species"),
        arith=dict(rule="AQ-004", sev="warn",
                   formula="06-01 + 30 d = 07-01",
                   harvest="harvest 06-20 · only 19 d",
                   bar_l="actual 19 d", bar_r="needs ≥ 30 d",
                   note="11 d short · arithmetic only"),
        strip=("issues[] 2 differences · skipped[] 2 not executed", "verdict stays human"),
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 30, 420, hx(s["accent"]),
               24 if skin == "light" else 38)
    img = glow(img, 90, 580, 300, hx(s["glow2"]),
               10 if skin == "light" else 16)

    d = ImageDraw.Draw(img)
    m = 64
    col_w = 596

    # ---- left column: kicker / title / value / sub / meta / footer -----------
    pill(img, (m, 56), H["kicker"], s, size=17)
    d = ImageDraw.Draw(img)

    title_size = fit("dsh-aqua-input-check", "mono_bold", col_w, 58, 48)
    d.text((m - 2, 118), "dsh-aqua-input-check", font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))

    vf = fit_lines(H["value"], "cjk_bold", col_w, 42, 34)
    for i, line in enumerate(H["value"]):
        d.text((m, 204 + i * 56), line, font=font(vf, "cjk_bold"),
               fill=hx(s["text"]))

    sf = font(22, "cjk")
    for i, line in enumerate(H["sub"]):
        require_w(line, 22, "cjk", col_w, "hero sub")
        d.text((m + 1, 334 + i * 34), line, font=sf, fill=hx(s["sub"]))

    require_w(H["meta"], 19, "cjk", col_w, "hero meta")
    require_w(H["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 428), H["meta"], font=font(19, "cjk"), fill=hx(s["faint"]))
    d.line([m + 1, 480, m + col_w - 4, 480], fill=hx(s["grid"]), width=2)
    d.text((m + 1, 494), H["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- right: the register card -------------------------------------------
    img = card(img, (700, 40, 1376, 320), s, radius=RADIUS, shadow=SHADOW)
    d = ImageDraw.Draw(img)
    d.text((724, 58), H["reg_title"], font=font(17, "cjk_bold"),
           fill=hx(s["accent"]))
    cw = measure(H["reg_chip"], 11, "cjk")
    chip(img, (1352 - int(cw) - 18, 54), H["reg_chip"], s["accent"], s["pill"],
         size=11)
    d = ImageDraw.Draw(img)
    d.text((724, 88), H["farm"], font=font(13, "cjk"), fill=hx(s["sub"]))
    require_w(H["farm"], 13, "cjk", 620, "farm header")

    # table
    x0, top = 724, 116
    xs, acc = [], x0
    for w in H["widths"]:
        xs.append(acc)
        acc += w
    x_end = acc
    d.rounded_rectangle([x0 - 8, top, x_end + 8, top + 32], radius=9,
                        fill=hx(s["band"]))
    for i, head in enumerate(H["headers"]):
        hs = 12.5 if lang == "zh" else 11.5
        require_w(head, hs, "cjk_bold", H["widths"][i] - 16, "table header")
        d.text((xs[i] + 10, top + 9), head, font=font(hs, "cjk_bold"),
               fill=hx(s["sub"]))
    row_h = 46
    for r, row in enumerate(H["rows"]):
        ry = top + 32 + r * row_h
        for i, value in enumerate(row):
            is_date = value.startswith("2026-")
            f = font(13, "mono") if is_date else font(15, "cjk")
            fill = s["text"]
            if i == 0 and r == 0:
                fill = s["mark"]
            if i == 2 and lang == "en":
                f = font(14, "cjk")
            require_w(value, 13 if is_date else (14 if i == 2 and lang == "en" else 15),
                      "mono" if is_date else "cjk", H["widths"][i] - 18, "table cell")
            d.text((xs[i] + 10, ry + 14), value, font=f, fill=hx(fill))
        if r < len(H["rows"]) - 1:
            d.line([x0, ry + row_h, x_end, ry + row_h], fill=hx(s["grid"]),
                   width=1)

    # the one ringed cell: both pond and species are blank on row 1
    cell = (xs[0] - 2, top + 32 + 4, xs[0] + H["widths"][0] - 16, top + 32 + row_h - 4)
    d.rounded_rectangle(cell, radius=9, fill=hx(s["mark_bg"]))
    dash_rect(d, cell, s["mark"], width=2, dash=7, gap=4)
    d.text((724, 300), H["note"], font=font(12.5, "cjk"), fill=hx(s["faint"]))
    require_w(H["note"], 12.5, "cjk", 628, "register note")

    # ---- right: finding card + withdrawal arithmetic card -------------------
    img = card(img, (700, 336, 1028, 480), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    A = H["issue"]
    d.text((722, 352), A["rule"], font=font(13.5, "mono_bold"),
           fill=hx(s["accent"]))
    w = measure(A["rule"], 13.5, "mono_bold")
    chip(img, (722 + int(w) + 8, 350), A["sev"], s["accent"], s["pill"], size=10)
    d = ImageDraw.Draw(img)
    d.text((722, 378), A["locator"], font=font(12, "cjk"), fill=hx(s["sub"]))
    d.text((722, 400), A["found"], font=font(13, "cjk"), fill=hx(s["text"]))
    d.text((722, 426), A["expected"], font=font(12.5, "cjk"), fill=hx(s["sub"]))
    d.text((722, 452), A["fix"], font=font(11.5, "cjk"), fill=hx(s["faint"]))
    for key, size, kind in (("locator", 12, "cjk"), ("found", 13, "cjk"),
                            ("expected", 12.5, "cjk"), ("fix", 11.5, "cjk")):
        require_w(A[key], size, kind, 288, f"issue {key}")

    img = card(img, (1040, 336, 1376, 480), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    B = H["arith"]
    d.text((1060, 352), B["rule"], font=font(13.5, "mono_bold"),
           fill=hx(s["accent"]))
    w = measure(B["rule"], 13.5, "mono_bold")
    chip(img, (1060 + int(w) + 8, 350), B["sev"], s["accent"], s["pill"], size=10)
    d = ImageDraw.Draw(img)
    d.text((1060, 376), B["formula"], font=font(13, "cjk"), fill=hx(s["text"]))
    d.text((1060, 400), B["harvest"], font=font(12.5, "cjk"), fill=hx(s["sub"]))

    # the arithmetic bar: 19 of the 30 days the record itself states
    bx0, bx1, by = 1060, 1356, 424
    d.rounded_rectangle([bx0, by, bx1, by + 9], radius=5, fill=hx(s["grid"]))
    fillw = int((bx1 - bx0) * 19 / 30)
    d.rounded_rectangle([bx0, by, bx0 + fillw, by + 9], radius=5,
                        fill=hx(s["mark"]))
    d.ellipse([bx0 + fillw - 4, by - 4, bx0 + fillw + 4, by + 13],
              fill=hx(s["mark"]))
    d.text((1060, 440), B["bar_l"], font=font(10.5, "cjk"), fill=hx(s["mark"]))
    rw = measure(B["bar_r"], 10.5, "cjk")
    d.text((1356 - rw, 440), B["bar_r"], font=font(10.5, "cjk"),
           fill=hx(s["faint"]))
    d.text((1060, 458), B["note"], font=font(11, "cjk"), fill=hx(s["faint"]))
    require_w(B["formula"], 13, "cjk", 300, "arithmetic formula")
    require_w(B["harvest"], 12.5, "cjk", 300, "arithmetic harvest")
    require_w(B["note"], 11, "cjk", 300, "arithmetic note")

    # ---- right: the report line ---------------------------------------------
    img = card(img, (700, 496, 1376, 546), s, radius=18, shadow=16)
    d = ImageDraw.Draw(img)
    d.text((724, 512), H["strip"][0], font=font(13.5, "cjk"),
           fill=hx(s["text"]))
    rw = measure(H["strip"][1], 13.5, "cjk")
    d.text((1352 - rw, 512), H["strip"][1], font=font(13.5, "cjk_bold"),
           fill=hx(s["accent2"]))
    strip_w = measure(H["strip"][0], 13.5, "cjk") + rw + 40
    if strip_w > 628:
        raise SystemExit(f"FATAL: hero report strip overflows ({strip_w:.1f}px)")

    name = f"dsh-aqua-input-check-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}×{HT})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", band_alt="#faf8fe",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", rule="#dcd8ea",
        card="#ffffff", shadow="0.10",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", band_alt="#1e2534",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", rule="#2b3348",
        card="#1b2231", shadow="0.45",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = ("'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace")

# rule id, severity, one-line description, columns read (1-based), default-skip
RULES = [
    ("AQ-001", "warn", "塘口与品种至少一项", [1], False),
    ("AQ-002", "warn", "有名称则须有用量·日期", [2, 3], False),
    ("AQ-003", "warn", "使用日期不晚于核对日", [3], False),
    ("AQ-004", "warn", "使用日期+休药期≤起捕", [3, 4, 5], False),
    ("AQ-005", "warn", "有投苗则须有来源·检疫", [6], False),
    ("AQ-006", "info", "类型取值随本机构口径", [7], True),
    ("AQ-007", "warn", "批次编号全表唯一", [8], False),
]
COLUMNS = [
    ("塘口", "品种"),        # pondNo + species
    ("投入品", "名称·用量"),  # inputName + inputQty
    ("使用", "日期"),        # usedAt
    ("休药期", "天数"),      # withdrawalDays
    ("起捕", "日期"),        # harvestAt
    ("苗种", "来源·检疫"),    # stockingAt + stockSource + quarantineNo
    ("投入品", "类型"),      # inputType
    ("批次", "编号"),        # batchNo
]
COL_W = [62, 66, 56, 56, 56, 72, 48, 44]


class Svg:
    """Tiny SVG writer that measures every label before it is emitted."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None, tracking: float | None = None) -> None:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        if mono and weight:
            kind = "mono_bold"
        if max_w is not None:
            w = measure(content, size, kind)
            if tracking:
                w += tracking * max(len(content) - 1, 0)
            if w > max_w + 0.4:
                self.overflows.append(
                    f"{content!r} needs {w:.1f}px > {max_w}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_CJK
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if tracking:
            attrs.append(f'letter-spacing="{tracking}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             fill: str = "none") -> None:
        attrs = [f'd="{d}"', f'fill="{fill}"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linecap="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        self.add(f'<path {" ".join(attrs)}/>')

    def chip(self, x_right: float, y: float, label: str, fg: str, bg: str,
             *, size: float = 11, pad: float = 9, height: float = 20,
             mono: bool = False, weight: int | None = None) -> float:
        """A pill anchored on its right edge; returns its left edge."""
        kind = "mono" if mono else "cjk"
        if weight:
            kind += "_bold"
        w = measure(label, size, kind) + pad * 2
        x = x_right - w
        self.rect(x, y, w, height, fill=bg, rx=height / 2)
        self.text(x + pad, y + height / 2 + size * 0.34, label, size, fg,
                  anchor="start", weight=weight, mono=mono)
        return x

    def svg(self, w: int, h: int, label: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-label="{escape(label)}">')
        return "\n".join([head, *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
          f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
          f'flood-color="#16122c" flood-opacity="{s["shadow"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add("</defs>")
    v.add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    v.text(44, 58, "dsh-aqua-input-check", 28, s["text"], weight=700, mono=True,
           max_w=620)
    v.text(44, 86, "aqua_input_check 读一份登记表：七条规则只看这些栏，差异回到行号与栏名；未执行的逐条说明。",
           15, s["sub"], max_w=820)
    v.chip(1056, 36, "规则包 v2026.1 · 7 条", s["accent"], s["band"],
           size=12, pad=12, height=26)

    # ---- matrix panel -------------------------------------------------------
    v.rect(44, 108, 682, 438, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(62, 132, "登记表 rows[]（JSON / YAML，只读）× 规则包", 12, s["faint"],
           max_w=470)
    v.text(708, 132, "列名已归一", 12, s["faint"], anchor="end", max_w=90)

    col_x = 250
    centers = []
    for w in COL_W:
        centers.append(col_x + w / 2)
        col_x += w

    # header band
    v.rect(250, 146, 460, 44, fill=s["band"], rx=9)
    v.text(62, 168, "规则 · 严重级", 12, s["faint"], max_w=120)
    for i, (l1, l2) in enumerate(COLUMNS):
        v.text(centers[i], 165, l1, 12, s["sub"], anchor="middle",
               max_w=COL_W[i] - 6)
        v.text(centers[i], 182, l2, 12, s["sub"], anchor="middle",
               max_w=COL_W[i] - 6)

    top = 190
    row_h = 44
    for k, (rid, sev, desc, cols, skipped) in enumerate(RULES):
        ry = top + k * row_h
        if k % 2 == 1:
            v.rect(56, ry, 658, row_h, fill=s["band_alt"])
        if k < len(RULES) - 1:
            v.line(56, ry + row_h, 714, ry + row_h, stroke=s["rule"], sw=1)

        v.text(62, ry + 18, rid, 13.5, s["text"], weight=700, mono=True)
        w = measure(rid, 13.5, "mono_bold")
        chip_fg = s["accent"] if sev == "warn" else s["faint"]
        v.chip(62 + w + 8 + 38, ry + 6, sev, chip_fg, s["band"],
               size=9.5, pad=7, height=16, weight=700)
        v.text(62, ry + 37, desc, 11.5, s["sub"], max_w=180)

        xs = [centers[c - 1] for c in cols]
        if len(xs) > 1:
            v.line(xs[0], ry + 22, xs[-1], ry + 22, stroke=s["accent"], sw=1.6,
                   opacity=0.32)
        for x in xs:
            if skipped:
                v.add(f'<circle cx="{x}" cy="{ry + 22}" r="5" fill="none" '
                      f'stroke="{s["accent"]}" stroke-width="1.8" opacity="0.85"/>')
            else:
                v.add(f'<circle cx="{x}" cy="{ry + 22}" r="5" '
                      f'fill="{s["accent"]}"/>')

    # legend
    v.line(62, 500, 708, 500, stroke=s["rule"], sw=1)
    v.text(62, 518, "实心点 = 该条规则读这一栏；连线 = 同一条规则把几栏放在一起读。",
           11, s["faint"], max_w=640)
    v.text(62, 535, "空心点 = 投入品类型取值口径未配置（values 为空），默认 skipped 并写明原因。",
           11, s["faint"], max_w=640)

    # ---- output channels ----------------------------------------------------
    v.rect(752, 118, 304, 182, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(772, 146, "issues[]", 14.5, s["accent"], weight=700, mono=True)
    v.chip(1036, 128, "2 条", s["accent"], s["band"], size=10.5, pad=8,
           height=18)

    v.text(772, 176, "AQ-001 · 第 1 行 · pondNo", 11.5, s["sub"], mono=True,
           max_w=250)
    v.text(772, 196, "pondNo、species 都为空", 12, s["text"], max_w=250)
    v.text(772, 232, "AQ-004 · 第 2 行 · harvestAt", 11.5, s["sub"], mono=True,
           max_w=250)
    v.text(772, 252, "19 天 < 记录自己写的 30 天", 12, s["text"], max_w=258)
    v.text(772, 284, "每条差异都带 行号 + 栏名 + 应填", 11, s["faint"], max_w=258)

    v.rect(752, 316, 304, 136, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(772, 344, "skipped[]", 14.5, s["sub"], weight=700, mono=True)
    v.chip(1036, 326, "2 条", s["sub"], s["band"], size=10.5, pad=8,
           height=18)
    v.text(772, 376, "AQ-006 · values 未配置", 11.5, s["text"], mono=True,
           max_w=250)
    v.text(772, 400, "AQ-007 · 材料没有批次编号列", 11.5, s["text"], mono=True,
           max_w=250)
    v.text(772, 432, "空 issues ≠ 没问题：两条通道一起读", 11, s["faint"],
           max_w=258)

    v.rect(752, 468, 304, 78, fill=s["card"], rx=18, stroke=s["accent"],
           sw=1.6, shadow=True)
    v.text(772, 496, "审核人", 13.5, s["text"], weight=700, max_w=120)
    v.text(772, 518, "结论不在报告里", 11.5, s["sub"], max_w=200)
    v.text(772, 536, "issues 与 skipped 一起读", 10.5, s["faint"], max_w=240)

    # manifold: matrix → two channels → reviewer
    v.path("M726 330 H738", stroke=s["accent"], sw=1.6)
    v.path("M738 209 V507", stroke=s["accent"], sw=1.6)
    for y in (209, 384, 507):
        v.line(738, y, 750, y, stroke=s["accent"], sw=1.6, marker="arr")

    # ---- footer -------------------------------------------------------------
    v.line(44, 564, 1056, 564, stroke=s["rule"], sw=1)
    v.text(44, 588,
           "严重级跟着证据走：derived-from-principle ≤ warn · institutional-configuration ≤ info；excerpt 必须是逐字引文",
           11.5, s["sub"], max_w=1012)
    v.text(44, 612,
           "config：rulesFile · disabledRules · onlyRules · timeoutMs ｜ 只读材料 · 无网络 · 不调用模型",
           11.5, s["faint"], max_w=1012)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " + "\n  ".join(v.overflows))
    return v.svg(W, H, "dsh-aqua-input-check 结构图：登记表的栏与七条规则组成的点阵，"
                       "输出分成 issues[] 与 skipped[] 两条通道，结论留给审核人")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"dsh-aqua-input-check-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100×660)")


if __name__ == "__main__":
    main()

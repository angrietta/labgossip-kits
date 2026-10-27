"""종말 예언 편: 자막·숫자·효과음 합성.
사실 출처 (원문 대조 완료, 기획 문서 lab-gossip-EP-종말예언-기획 참고):
  von Foerster, Mora, Amiot, Science 132:1291 (1960-11-04): U = 2026.87 ± 5.50, N = 1.79e11/(2026.87 - t)^0.99, "squeezed to death"
  24 estimates / 2,000 years / accurate until ~1993 / birth rate today < half of 1960: The Conversation (A. MacEachern) via ScienceDaily 2026-10-16
  ~8.3 billion today: Popular Science 2026-10-13
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine")); sys.path.insert(0, HERE)
from comp import *
from timeline import *

def fmt_b(n):
    b = n / 1e9
    return f"{b:.1f}B" if b < 20 else f"{b:.0f}B"

def frame(f, img):
    tag(img, 8, "CLAY MODEL")
    # hook
    pop(img, sprite("SCIENCE PICKED", ANTON(118), WHITE), W / 2, 330, f, 4, HOOK[1])
    pop(img, sprite(" THE END OF THE WORLD ", ANTON(92), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 470, f, 12, HOOK[1])
    pop(img, sprite("(Science, 1960. A real paper.)", ARCH(36), WHITE, stroke=6), W / 2, 580, f, 40, HOOK[1])
    # setup
    for i, t in enumerate(("3 SCIENTISTS", "24 POPULATION COUNTS", "2,000 YEARS OF DATA")):
        pop(img, sprite(t, ANTON(84), WHITE), W / 2, 330 + i * 105, f, SETUP[0] + 14 + i * 14, EXP1[0] - 4)
    # experiment: year + formula counter
    if EXP1[0] <= f < REAL:
        y = year_at(f); n = formula(y)
        a = seg(f, EXP1[0], EXP1[0] + 6)
        put(img, sprite(f"YEAR {int(y)}", ANTON(120), WHITE), W / 2, 300, 1, a)
        put(img, sprite(f" FORMULA SAYS: {fmt_b(n)} PEOPLE ", ANTON(70), WHITE, stroke=0, box=RED, pad=(14, 6)), W / 2, 430, 1, a)
        put(img, sprite("each red ball = 1 billion people", ARCH(30), WHITE, stroke=6), W / 2, 1700, 1, a)
    pop(img, sprite("SPOT ON FOR 30+ YEARS", ANTON(80), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 560, f, EXP1[1] - 24, EXP2[0] + 20)
    pop(img, sprite(" NOV 13, 2026: INFINITY ", ANTON(84), INK, stroke=0, box=YEL, pad=(14, 6), rot=2), W / 2, 560, f, EXP2[1] - 6, REAL - 2)
    pop(img, sprite('"They will be squeezed to death."', ARCH(38), WHITE, stroke=7), W / 2, 1560, f, EXP2[1] + 6, REAL - 2)
    pop(img, sprite("— the 1960 paper", ARCH(30), WHITE, stroke=6), W / 2, 1615, f, EXP2[1] + 10, REAL - 2)
    # reveal
    if f >= REAL and f < OUTRO[0]:
        a = seg(f, REAL, REAL + 6)
        put(img, sprite("FORMULA: 96B", ANTON(64), RED, stroke=8), W / 2, 300, 1, a)
        if f >= REAL + 8:
            sp = sprite("FORMULA: 96B", ANTON(64), RED, stroke=8); k = seg(f, REAL + 8, REAL + 14)
            from PIL import ImageDraw
            d = ImageDraw.Draw(img); x0 = W / 2 - sp.width / 2 + 10
            d.line([(x0, 300), (x0 + (sp.width - 20) * k, 300)], fill=WHITE, width=10)
    pop(img, sprite("REAL WORLD: ~8.3B", ANTON(110), WHITE), W / 2, 420, f, REAL + 14, OUTRO[0])
    pop(img, sprite(" IT BROKE AROUND 1993 ", ANTON(76), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 560, f, REAL + 34, PLATE - 4)
    pop(img, sprite("WHY? BIRTH RATE TODAY:", ANTON(76), WHITE), W / 2, 560, f, PLATE + 6, OUTRO[0])
    pop(img, sprite(" LESS THAN HALF OF 1960 ", ANTON(80), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 670, f, PLATE + 16, OUTRO[0])
    # the catch
    pop(img, sprite(" THE CATCH? ", ANTON(96), WHITE, stroke=0, box=RED, pad=(14, 6), rot=-3), W / 2, 330, f, OUTRO[0] + 8)
    pop(img, sprite("THEY GAVE ±5.5 YEARS.", ANTON(84), WHITE), W / 2, 460, f, OUTRO[0] + 18)
    pop(img, sprite(" SO... SEE YOU IN 2032? ", ANTON(80), INK, stroke=0, box=YEL, pad=(14, 6), rot=2), W / 2, 580, f, FLIP_2032 + 12)
    wrap_lines(img, ["von Foerster, Mora & Amiot, Science 132:1291 (1960)",
                     "Formula: N = 1.79e11 / (2026.87 - year)^0.99",
                     "Real population ~8.3B (2026): Popular Science"], ARCH(24), 1720, f, FLIP_2032 + 20, stroke=5)
    return img

def sfx(m):
    m.bed(F_END, skip=[(EXP2[1] - 20, SLAM + 20)])
    for f0 in CAL_FLIPS + [FLIP_2032]:
        w = m.noise(0.12, 0.12, 6); m.add(m.at(f0 + 3), w)
    m.add(m.at(HOOK[1] - 36), m.thud(0.5, 70, 40, 0.35))
    m.add(m.at(CIRCLE[0]), m.sweep(700, 1100, 0.5, 0.08, 2))
    for f0 in bead_drop_frames()[:40]:
        m.add(m.at(f0 + 5), m.tone(1500, 0.04, 0.06, 60))
    hum = m.sweep(60, 110, (EXP2[1] - EXP1[0]) / FPS, 0.05, 0)
    m.add(m.at(EXP1[0]), hum)
    m.add(m.at(SLAM - 6), m.sweep(520, 260, 0.6, 0.12, 3))            # brake groan (soft)
    m.add(m.at(SLAM), m.thud(0.9))
    for k in range(10): m.add(m.at(REAL + 4 + k * 5), m.tone(900 + 60 * k, 0.05, 0.08, 50))   # pops
    for k, fq in enumerate((1046, 1318, 1568)): m.add(m.at(REAL + 14) + k * 3000, m.tone(fq, 0.5, 0.13, 5))
    m.add(m.at(PLATE + 4), m.noise(0.2, 0.15, 10)); m.add(m.at(PLATE + 26), m.thud(0.5, 300, 120, 0.25, 12))
    m.add(m.at(OUTRO[0] + 8), m.tone(523, 0.3, 0.2, 10)); m.add(m.at(FLIP_2032 + 12), m.tone(988, 0.5, 0.2, 5))

if __name__ == "__main__":
    main(HERE, F_END, frame, sfx, "doomsday.mp4")

"""덕트 테이프 편: 자막·숫자·효과음 합성.
사실 (원문 대조): University of Hull 실험, Flood Re 의뢰, 2026년 10월 발표 (GadgetReview 2026-10-19 / Insurance Business UK)
  - 물 5cm씩 최대 60cm, 목재·uPVC·복합 소재 문
  - 덕트 테이프: 무방비 문 대비 누수 "approximately 97 to 98 percent" 감소, 고무 테이프 "around 99 percent"
  - 모래주머니 54개 + 비닐: "up to about 70 percent"
  - 바깥쪽에 붙이고, 바깥으로 열리는 문일수록 효과가 좋았음. 원 누수량은 공개되지 않음 → 안쪽 물높이는 비율을 나타낸 그림
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine")); sys.path.insert(0, HERE)
from comp import *
from timeline import *

AN = json.load(open(os.path.join(HERE, "out", "anchors.json")))
TIGHT_ON, TIGHT_OFF = RESULT[0] + 70, CATCH[0] + 14       # camera is tight on the tape row here

def row_label(img, i, text, f, f0, f1, box=WHITE, fill=INK):
    x, y = AN[f"row{i}"][0] * W, AN[f"row{i}"][1] * H
    sp = sprite(f" {text} ", ANTON(46), fill, stroke=0, box=box, pad=(8, 3))
    if f0 <= f < f1 + 3:
        a = seg(f, f0, f0 + 5) * (1 - seg(f, f1, f1 + 3))
        put(img, sp, x + sp.width / 2 - 10, y, 1, a)

def result(img, i, text, f, f0, f1, box):
    x, y = AN[f"in{i}"][0] * W, AN[f"in{i}"][1] * H
    sp = sprite(f" {text} ", ANTON(58), INK if box != RED else WHITE, stroke=0, box=box, pad=(10, 4), rot=-3)
    x = min(x, W - sp.width / 2 - 24)                  # keep long labels fully on screen
    pop(img, sp, x, y, f, f0, f1)

def frame(f, img):
    tag(img, 9, "FLOOD LAB")
    # hook
    pop(img, sprite("SANDBAGS", ANTON(140), WHITE), W / 2, 330, f, 4, HOOK[1])
    pop(img, sprite("vs.", ANTON(70), WHITE), W / 2, 450, f, 30, HOOK[1])
    pop(img, sprite(" A ROLL OF DUCT TAPE ", ANTON(92), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 560, f, TAPE_ROLL + 4, HOOK[1])
    # contestant intro
    # two text blocks per contestant, 3 s each (Codex review round 1: readability)
    for k, ((f0, f1), (name, note)) in enumerate(zip(INTRO_ITEMS, [
            ("AN ORDINARY FRONT DOOR", "no protection"),
            ("54 SANDBAGS + PLASTIC", "the classic defense"),
            ("ONE ROLL OF DUCT TAPE", "stuck on from outside")])):
        pop(img, sprite(f" #{k + 1}  {name} ", ANTON(74), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 330, f, f0 + 3, f1 - 3)
        pop(img, sprite(note, ARCH(40), WHITE, stroke=6), W / 2, 450, f, f0 + 10, f1 - 3)
    # setup
    pop(img, sprite("SAME DOOR. 3 WAYS.", ANTON(92), WHITE), W / 2, 300, f, SETUP[0] + 10, FILL[0] + 30)
    pop(img, sprite("University of Hull flood lab tests", ARCH(36), WHITE, stroke=6), W / 2, 395, f, SETUP[0] + 22, FILL[0] + 30)
    pop(img, sprite(" WATER UP TO 60 CM ", ANTON(74), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 490, f, SETUP[0] + 34, FILL[0] + 30)
    # water counter
    if FILL[0] + 30 <= f < TIGHT_ON:
        a = seg(f, FILL[0] + 30, FILL[0] + 36) * (1 - seg(f, TIGHT_ON - 4, TIGHT_ON))
        put(img, sprite(f"WATER: {water_cm(f)} CM", ANTON(110), WHITE), W / 2, 330, 1, a)
        put(img, sprite("outside  |  door  |  inside", ARCH(30), WHITE, stroke=6), W / 2, 440, 1, a)
    # row labels (wide shot only)
    for i, (name, frac) in enumerate(ROWS):
        lab = name if i != 1 else "54 SANDBAGS + PLASTIC"
        row_label(img, i, lab, f, SETUP[0] + 60 + i * 6, TIGHT_ON - 4, box=YEL if i == 2 else WHITE)
        row_label(img, i, lab, f, CATCH[0] + 20, F_END + 10, box=YEL if i == 2 else WHITE)
    result(img, 0, "LEAK: 100%", f, RESULT[0] + 6, TIGHT_ON - 4, RED)
    result(img, 1, "BLOCKED UP TO ~70%", f, RESULT[0] + 22, TIGHT_ON - 4, WHITE)   # source: "up to about 70 percent"
    result(img, 2, "BLOCKED 97-98%", f, RESULT[0] + 40, TIGHT_ON - 4, YEL)
    # tight on the tape row
    pop(img, sprite("DUCT TAPE", ANTON(120), WHITE), W / 2, 330, f, TIGHT_ON + 4, TIGHT_OFF)
    pop(img, sprite(" BLOCKED 97-98% ", ANTON(100), INK, stroke=0, box=YEL, pad=(14, 6), rot=-2), W / 2, 470, f, TIGHT_ON + 10, TIGHT_OFF)
    pop(img, sprite("54 sandbags: up to ~70%  ·  rubber tape: ~99%", ARCH(32), WHITE, stroke=6), W / 2, 590, f, TIGHT_ON + 22, TIGHT_OFF)
    # the catch
    pop(img, sprite(" THE CATCH? ", ANTON(92), WHITE, stroke=0, box=RED, pad=(14, 6), rot=-3), W / 2, 250, f, CATCH[0] + 18)
    pop(img, sprite("BEST ON THE OUTSIDE. DEPENDS ON THE DOOR.", ANTON(56), WHITE), W / 2, 360, f, CATCH[0] + 28)
    pop(img, sprite(" TAPE BUYS TIME. IT'S NOT A FLOOD PLAN. ", ANTON(56), INK, stroke=0, box=YEL, pad=(12, 5), rot=1), W / 2, 450, f, CATCH[0] + 44)
    wrap_lines(img, ["University of Hull tests for Flood Re (Oct 2026)",
                     "% = leak reduction vs. an unprotected door, as reported",
                     "Raw volumes not published: inside water levels are illustrative"], ARCH(24), 1745, f, CATCH[0] + 50, stroke=5)
    return img

def sfx(m):
    m.bed(F_END, skip=[(RESULT[0] - 10, RESULT[0] + 20), (INTRO[0], INTRO[1])])
    for k in range(18): m.add(m.at(4 + 2 * k + 4), m.thud(0.35, 120, 50, 0.25, 12))    # sandbags
    for k, (f0, f1) in enumerate(INTRO_ITEMS):                                                    # contestant chimes
        m.add(m.at(f0 + 2), m.tone((523, 659, 784)[k], 0.4, 0.18, 6)); m.add(m.at(f0 + 6), m.noise(0.3, 0.2))
    m.add(m.at(TAPE_ROLL + 5), m.thud(0.5, 260, 90, 0.3, 9)); m.add(m.at(TAPE_ROLL + 13), m.thud(0.3, 300, 110, 0.2, 12))
    for f0 in TAPE_STRIPS:                                                                      # tape rip + slap
        m.add(m.at(f0 - 6), m.noise(0.25, 0.25))
        m.add(m.at(f0 + 3), m.thud(0.3, 200, 80, 0.12, 20))
    rng = np.random.default_rng(9)                                                              # soft bubbles while water rises
    for f0 in range(FILL[0] + 6, FILL[1], 9):
        m.add(m.at(f0 + int(rng.integers(0, 6))), m.bubble(0.05 + 0.04 * rng.random()))
    for k in range(13): m.add(m.at(FILL[0] + 30 + k * 20), m.tone(700 + 40 * k, 0.05, 0.06, 40))  # 5 cm ticks
    m.add(m.at(RESULT[0] + 6), m.thud(0.4, 90, 40, 0.3)); m.add(m.at(RESULT[0] + 22), m.tone(523, 0.2, 0.15, 10))
    for k, fq in enumerate((1046, 1318, 1568)): m.add(m.at(RESULT[0] + 40) + k * 3000, m.tone(fq, 0.5, 0.13, 5))
    m.add(m.at(CATCH[0] + 18), m.tone(523, 0.3, 0.2, 10)); m.add(m.at(CATCH[0] + 44), m.tone(988, 0.5, 0.2, 5))

if __name__ == "__main__":
    main(HERE, F_END, frame, sfx, "ducttape.mp4")

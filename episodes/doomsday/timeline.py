"""종말 예언 편: 장면과 자막이 함께 쓰는 시간표·숫자 (여기만 고치면 둘 다 바뀜).
공식 출처: von Foerster, Mora, Amiot, Science 132:1291 (1960) 식 (11): N = 1.79e11 / (2026.87 - t)^0.99
"""
FPS, F_END = 24, 768

# 장면 구간 (프레임)
HOOK = (1, 72)          # 달력 넘김 → FRI 13 NOV 2026
SETUP = (72, 168)       # 카메라 뒤로, 프레스·지구 공개
EXP1 = (168, 312)       # 1960 → 1993 (공식이 현실과 맞던 시기)
EXP2 = (312, 456)       # 1993 → 2025 (공식 폭주)
SLAM = 480              # 프레스가 지구 바로 위에서 정지
REAL = 500              # 구슬이 실제 인구만 남음
PLATE = 610             # "1960 FORMULA" 판이 떨어짐
OUTRO = (696, 768)      # 달력 2026 → 2032

CAL_FLIPS = [10, 18, 26]          # 앞장 3장이 넘어가는 시작 프레임
CIRCLE = (38, 52)                 # 13 주위 빨간 동그라미 그려짐
FLIP_2032 = 716

MAX_BEADS = 96                     # 구슬 1개 = 10억 명. 2025년 공식값 963억 → 96개
REAL_BEADS = 8                     # 실제 약 83억 → 8개

def formula(year):
    return 1.79e11 / (2026.87 - year) ** 0.99

def year_at(f):
    """Frame -> year shown on the counter."""
    if f < EXP1[0]: return 1960.0
    if f < EXP1[1]: return 1960 + (f - EXP1[0]) / (EXP1[1] - EXP1[0]) * 33
    if f < EXP2[1]: return 1993 + (f - EXP2[0]) / (EXP2[1] - EXP2[0]) * 32
    return 2025.0

def beads_at(f):
    return min(MAX_BEADS, int(round(formula(year_at(f)) / 1e9)))

def bead_drop_frames():
    """Frame at which bead i (0-based) starts to fall."""
    out, have = [], 0
    for f in range(EXP1[0], EXP2[1] + 1):
        n = beads_at(f)
        while have < n:
            out.append(f); have += 1
    return out

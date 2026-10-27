"""덕트 테이프 편: 장면·자막 공용 시간표와 숫자.
출처: University of Hull 실험(Flood Re 의뢰, 2026년 10월 Flood Action Week 발표) — GadgetReview 2026-10-19, Insurance Business UK.
  덕트 테이프: 무방비 문 대비 누수 약 97~98% 감소 / 고무 테이프 약 99% / 모래주머니 54개 + 비닐: 최대 약 70%
  물 높이 5cm씩 최대 60cm, 바깥쪽에 붙이고 바깥으로 열리는 문일수록 효과가 좋았음. 원 누수량(리터)은 공개 안 됨.
"""
FPS, F_END = 24, 864

HOOK = (1, 84)          # 모래주머니 18개 쿵쿵(4~44프레임), 테이프 롤 통, 테이프 착
INTRO = (84, 228)       # 참가자 소개: 회전대 위에 문 / 모래주머니+비닐 / 덕트 테이프가 차례로
INTRO_ITEMS = [(84, 132), (132, 180), (180, 228)]
SETUP = (228, 300)      # 카메라 뒤로 → 3단 실험대
FILL = (300, 588)       # 바깥 물 0 → 60cm, 안쪽 누수
RESULT = (588, 744)     # 줄별 결과
CATCH = (744, 864)

TAPE_ROLL = 46          # 테이프 롤이 떨어지는 프레임
TAPE_STRIPS = [58, 64]  # 테이프가 붙는 프레임

ROWS = [                # 위에서 아래로: 이름, 남는 누수 비율(무방비 = 1)
    ("NO PROTECTION", 1.00),
    ("54 SANDBAGS", 0.30),   # "up to about 70 percent" 감소 → 약 30% 남음
    ("DUCT TAPE", 0.025),    # "approximately 97 to 98 percent" 감소 → 약 2~3% 남음
]

def water_frac(f):
    """0..1 of the 60 cm max, eased."""
    if f <= FILL[0]: return 0.0
    if f >= FILL[1]: return 1.0
    t = (f - FILL[0]) / (FILL[1] - FILL[0]); return t * t * (3 - 2 * t)

def water_cm(f):
    return int(round(water_frac(f) * 60 / 5) * 5)   # 5 cm steps, like the test

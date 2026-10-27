# LAB GOSSIP kits

LAB GOSSIP 쇼츠의 점토 실험 영상 원본 코드. Claude가 만들고, Codex(ChatGPT)가 검토하고, 사람은 최종 판단만 한다.

## 한 바퀴 (리뷰 1회)
1. Claude가 준 새 파일을 이 폴더에 덮어쓰기
2. `2_SEND_FOR_REVIEW.bat` 더블클릭 → PR 생성 + `@codex review` 요청
3. 몇 분 뒤 Claude에게 "리뷰 봐줘" → Claude가 `reviews` 브랜치의 리뷰 기록을 읽고 수정본 제공
4. 괜찮으면 `3_MERGE.bat` (main에 합치기). 수정본을 받았으면 1번부터 다시

## 구조
- `AGENTS.md` — Codex 검토 규칙 (숫자·출처 대조 우선, 색·구도는 검토 제외)
- `.github/workflows/save-reviews.yml` — PR 리뷰·댓글을 `reviews` 브랜치의 `reviews/pr-<번호>.md`로 저장
- `engine/` 공용 점토 엔진 · `episodes/<편>/` 장면·자막·시간표 · `fonts/` (SIL OFL 폰트)

렌더는 편별 렌더 키트(LABGOSSIP_<편>.zip)로 한다. 이 저장소는 원본 관리와 검토용.

# LAB GOSSIP kits

LAB GOSSIP 쇼츠의 점토 실험 영상 원본 코드. Claude가 만들고, Codex(ChatGPT)가 검토하고, 사람은 최종 판단만 한다.

## 리뷰 흐름 (PR 하나당 최대 3회)
1. Claude가 준 새 파일을 이 폴더에 덮어쓰기
2. `2_SEND_FOR_REVIEW.bat` 더블클릭 → 처음엔 PR을 만들고 round 1/3 요청, 같은 PR이 열려 있으면 수정본을 올리고 round 2/3, 3/3 요청
3. 몇 분 뒤 Claude에게 "리뷰 봐줘" → Claude가 `reviews` 브랜치의 리뷰 기록을 읽고 수정본 제공
4. 3회가 끝났거나 Codex가 `LGTM`이면 `3_MERGE.bat` (main에 합치기). 끝까지 남은 이견은 사람이 결정

## 구조
- `AGENTS.md` — Codex 검토 규칙 (사실 > 렌더 버그 > 연출: 훅·속도·가독성·명확성·카메라·색 대비·소리) + 라운드 규칙
- `episodes/<편>/STORYBOARD.md`, `preview.png` — 연출 검토용 장면표와 미리보기
- `.github/workflows/save-reviews.yml` — PR 리뷰·댓글을 `reviews` 브랜치의 `reviews/pr-<번호>.md`로 저장
- `engine/` 공용 점토 엔진 · `episodes/<편>/` 장면·자막·시간표 · `fonts/` (SIL OFL 폰트)

렌더는 편별 렌더 키트(LABGOSSIP_<편>.zip)로 한다. 이 저장소는 원본 관리와 검토용.

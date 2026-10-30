# LAB GOSSIP kits — notes for AI reviewers

This repo holds the source for LAB GOSSIP YouTube Shorts: clay-style 3D "lab experiment" videos about new research,
rendered with Blender (Python `bpy`), 1080x1920, 24 fps, 30–45 seconds. Audience: curious adults scrolling Shorts.
Channel rule: **the tone can be playful, every sentence must be true.**

- `engine/clay.py` — shared Blender helpers (materials, studio, colour palettes, render settings)
- `engine/comp.py` — captions, sound design, summary sheet and mp4 assembly (Pillow + ffmpeg)
- `episodes/<name>/timeline.py` — frame timings and the numbers shown on screen, with sources in the docstring
- `episodes/<name>/scene.py` — the 3D scene; `composite.py` — captions and sound for that episode
- `episodes/<name>/STORYBOARD.md` — shot-by-shot description (time, camera, on-screen text, sound, intent)
- `episodes/<name>/preview.png` — low-resolution render of key frames with captions (look at it)

## Code Review Rules

Write the review in **Korean**. Order findings by severity:
**사실 오류 > 렌더를 망치는 버그 > 연출 문제 > 오해 소지 > 개선 제안.**
For each finding give the file and line (or the storyboard time), what is wrong, and a concrete fix
(new numbers, new frame range, new wording). At most 12 findings.

### A. Facts (highest priority)
1. Every number, date, percentage or quote in a caption (`composite.py`) must match the source notes at the top of
   that episode's `composite.py` / `timeline.py`. Flag on-screen numbers with no source note, or wording stronger or
   more precise than the source (source "up to about 70 percent" → caption must not say "70%").
2. Flag overstated framing: "proves", "cures", one study presented as consensus, animal or cell results presented as
   human results, correlation presented as cause, illustrative values not labelled as illustrative.
   Every episode must end with a readable "THE CATCH?" limitation.

### B. Direction (연출) — use STORYBOARD.md, preview.png and the frame numbers in timeline.py
3. **Hook:** the question or claim is on screen within the first 1.5 s, and something moves within the first 1 s.
4. **Pacing:** no stretch longer than ~4 s without a visual change (new action, camera move, cut, or caption).
   Flag beats that drag or are too fast to follow.
5. **Readability:** each caption stays on screen long enough to read (about 4 words per second, minimum 1 s);
   no more than two text blocks competing at once; the key number is the largest text on screen;
   text must not be cut off or sit on top of the object it describes.
6. **Clarity:** a viewer with no context can tell what every object on screen is and what is being compared.
   Flag any object, unit or scale that is never introduced.
7. **Camera:** moves must be motivated (follow the action or reveal something); flag moves that are too fast,
   cuts that hide the key moment, or framing that crops the key object at the key moment.
8. **Colour and contrast:** captions readable against the episode palette (see `PALETTES` in `engine/clay.py`);
   the palette fits the topic's mood; channel constants stay consistent (yellow/red caption boxes, Anton font,
   "LAB GOSSIP" tag).
9. **Sound:** effects sync with the visual event they belong to (frame numbers in `sfx()`); no harsh noise or
   sudden loud peaks; the music bed leaves room for key moments.

### C. Bugs
10. Blender 5.x API misuse, keyframes out of order, objects never shown/hidden, captions after `F_END`,
    Windows path or `.bat` problems, anything that would crash or ruin a full render.

### Out of scope
Code style and formatting nits. Do not propose switching away from Blender or from code-generated animation.

## Review rounds (max 3 per pull request)
The request comment says which round it is (`round 1/3` …).
- **Round 1:** full review using all rules above.
- **Round 2:** check whether the round-1 findings were fixed correctly; report new problems only if they are
  사실 오류, 렌더 버그 or clear 연출 problems.
- **Round 3:** only blockers (사실 오류, 렌더 버그). If none, reply exactly `LGTM` with a one-line summary.
  Anything still disputed after round 3 is decided by the human owner, not by another review.

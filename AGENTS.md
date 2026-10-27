# LAB GOSSIP kits — notes for AI reviewers

This repo holds the source for LAB GOSSIP YouTube Shorts: clay-style 3D "lab experiment" videos about new research,
rendered with Blender (Python `bpy`). Channel rule: **the tone can be playful, every sentence must be true.**

- `engine/clay.py` — shared Blender helpers (materials, studio, palettes, render settings)
- `engine/comp.py` — captions, sound design, summary sheet and mp4 assembly (Pillow + ffmpeg)
- `episodes/<name>/timeline.py` — frame timings and the numbers shown on screen, with sources in the docstring
- `episodes/<name>/scene.py` — the 3D scene; `composite.py` — captions and sound for that episode

## Code Review Rules

Write the review in **Korean**. Order findings by severity: 사실 오류 > 버그 > 오해 소지 > 개선 제안.
For each finding give the file and line, what is wrong, and a concrete fix.

1. **Numbers and claims (highest priority).** Every number, date, percentage or quote that appears in a caption
   (`composite.py`) must match the source notes at the top of that episode's `composite.py` / `timeline.py`.
   Flag any on-screen number that has no source note, or that is stronger or more precise than the source
   (e.g. source says "up to about 70 percent" but caption says "70%").
2. **Honest framing.** Flag wording that overstates the evidence ("proves", "cures", "scientists say" for one study),
   animal or cell results presented as human results, correlation presented as cause, and values that are drawn
   for illustration but not labelled as illustrative. Every episode must end with a "THE CATCH?" limitation.
3. **Caption timing.** Captions that overlap in the same screen area at the same time, captions that appear after
   `F_END`, or text likely to be cut off at 1080x1920.
4. **Bugs.** Blender 5.x API misuse, keyframes out of order, objects never shown/hidden, division by zero,
   Windows path or `.bat` problems, anything that would crash a full render.
5. **Do not review:** colours, camera framing, art direction, or formatting/style nits. Those are judged by watching the video.

Keep it short: at most 10 findings. If nothing is wrong in a category, skip it.

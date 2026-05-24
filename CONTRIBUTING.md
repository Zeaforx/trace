# Contributing to Trace

Thanks for wanting to contribute! Trace is intentionally minimal — **contributors only add concept files**. You never need to touch `server.py`, the web templates, or `style.css`. The web UI and server are stable infrastructure; new knowledge lives entirely in `animations/` and `concepts.json`.

---

## Philosophy

- One animation per concept, fully self-contained
- Step-through by default — students control the pace
- Consistent look and controls across every animation
- Zero magic: plain Python + Pygame, no frameworks

---

## Step-by-step: Adding a New Concept

### 1. Create your file

Place it in the right course folder under `animations/`:

```
animations/
├── data-structures/   ← arrays, linked lists, trees, heaps, …
└── algorithms/        ← sorting, searching, graph traversal, …
```

Name it with underscores: `merge_sort.py`, `dijkstra.py`, etc.

### 2. Use argparse for parameters

Every animation must accept its inputs as CLI flags with sensible defaults. Users shouldn't need to edit source code.

```python
parser = argparse.ArgumentParser(description="Trace — <Your Concept>")
parser.add_argument("--size", type=int, default=10, help="…")
args = parser.parse_args()
```

### 3. Follow the Pygame conventions

- Same controls: `SPACE` = next step, `R` = reset, `Q` = quit
- Same info bar at top (step counter, relevant stats)
- Same instruction bar at bottom (see style guide below)
- Window title: `"Trace — <Concept Name>"`

### 4. Register it in `concepts.json`

Add an entry to the matching course's `"concepts"` array:

```json
{
  "id": "merge_sort",
  "name": "Merge Sort",
  "description": "Visualize the divide-and-conquer merge process",
  "file": "animations/data-structures/merge_sort.py",
  "params": [
    {
      "name": "size",
      "type": "int",
      "default": 10,
      "description": "Number of elements to sort"
    }
  ]
}
```

If your concept belongs to a new course, add a new course object in `"courses"`.

### 5. Test it standalone

```bash
# No args — must work with defaults
python animations/data-structures/merge_sort.py

# With args
python animations/data-structures/merge_sort.py --size 20

# Via web UI
uvicorn server:app --reload   # then open localhost:8000
```

### 6. Open a PR

Follow the checklist at the bottom of this file.

---

## Minimal Starter Template

Copy this and fill in the blanks:

```python
"""
Trace — <Concept Name>
SPACE : next step
R     : reset
Q     : quit
"""

import argparse
import sys

import pygame

# ── Visual constants (copy exactly — keeps the style consistent) ──────────────
BG         = (13,  13,  13)
TEXT_COLOR = (226, 232, 240)
MUTED      = (100, 116, 139)
ACCENT     = (167, 139, 250)
HIGHLIGHT  = (124, 106, 247)   # purple  — active element
SUCCESS    = (52,  211, 153)   # green   — done / confirmed
WARNING    = (247, 180,  60)   # amber   — swap / special action

FONT_SIZE  = 14
BOTTOM_BAR = 40
INFO_HEIGHT = 56


def main():
    parser = argparse.ArgumentParser(description="Trace — <Concept Name>")
    # Add your params here:
    # parser.add_argument("--size", type=int, default=10, help="…")
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_caption("Trace — <Concept Name>")

    win_w, win_h = 900, 560
    screen = pygame.display.set_mode((win_w, win_h))
    font       = pygame.font.SysFont("monospace", FONT_SIZE + 2, bold=True)
    small_font = pygame.font.SysFont("monospace", FONT_SIZE - 1)

    clock = pygame.time.Clock()

    # ── Your state here ────────────────────────────────────────────────────────
    step = 0

    def draw():
        screen.fill(BG)

        # ── Your drawing logic here ────────────────────────────────────────────

        # Top info bar
        info = font.render(f"Step {step}", True, TEXT_COLOR)
        screen.blit(info, (20, 16))

        # Bottom instruction bar (required)
        instr = small_font.render(
            "SPACE: next step   |   R: reset   |   Q: quit", True, MUTED
        )
        pygame.draw.line(screen, (30, 30, 30),
                         (0, win_h - BOTTOM_BAR), (win_w, win_h - BOTTOM_BAR))
        screen.blit(instr, (win_w // 2 - instr.get_width() // 2,
                             win_h - BOTTOM_BAR + 12))

        pygame.display.flip()

    draw()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()

                elif event.key == pygame.K_r:
                    step = 0
                    # reset your state

                elif event.key == pygame.K_SPACE:
                    step += 1
                    # advance your state

                draw()

        clock.tick(60)


if __name__ == "__main__":
    main()
```

---

## Visual Style Guide

### Colors

| Purpose                | Value              | When to use                              |
|------------------------|--------------------|------------------------------------------|
| Background             | `(13, 13, 13)`     | `screen.fill(BG)`                        |
| Default element        | `(70, 80, 100)`    | Bars, nodes in idle state                |
| Active / highlight     | `(124, 106, 247)`  | Current pointer, traversal path          |
| Swap / special action  | `(247, 180, 60)`   | Swap pair, newly visited                 |
| Confirmed / done       | `(52, 211, 153)`   | Sorted bars, inserted node               |
| Body text              | `(226, 232, 240)`  | Labels, values                           |
| Muted / secondary      | `(100, 116, 139)`  | Step counts, instructions                |
| Accent (headers)       | `(167, 139, 250)`  | Top-bar status when complete             |

### Fonts

Always use `pygame.font.SysFont("monospace", ...)` — no external font files:

```python
font       = pygame.font.SysFont("monospace", 16, bold=True)   # info bar
small_font = pygame.font.SysFont("monospace", 13)              # instructions
```

### Bottom instruction bar (required on every animation)

```python
BOTTOM_BAR = 40

instr = small_font.render(
    "SPACE: next step   |   R: reset   |   Q: quit", True, MUTED
)
pygame.draw.line(screen, (30, 30, 30),
                 (0, win_h - BOTTOM_BAR), (win_w, win_h - BOTTOM_BAR))
screen.blit(instr, (win_w // 2 - instr.get_width() // 2,
                     win_h - BOTTOM_BAR + 12))
```

### Top info bar

Reserve `INFO_HEIGHT = 56` pixels at the top for step counter and stats. Draw text at `y=16` (bold label) and `y=36` (smaller stats).

---

## PR Checklist

Before submitting:

- [ ] Animation file is in the correct `animations/<course>/` folder
- [ ] File is completely self-contained (no imports from other project files)
- [ ] `python animations/<course>/<file>.py` works with no arguments
- [ ] `python animations/<course>/<file>.py --<param> <value>` works
- [ ] `SPACE` steps through the concept, `R` resets, `Q` quits
- [ ] Window title is `"Trace — <Concept Name>"`
- [ ] Bottom instruction bar is present
- [ ] Colors and fonts match the style guide
- [ ] Concept is registered in `concepts.json` with correct `file` path and `params`
- [ ] Web UI launches it correctly (tested via `uvicorn server:app --reload`)
- [ ] No leftover `print()` debug statements

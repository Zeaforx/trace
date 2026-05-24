"""
Trace — Bubble Sort Visualizer
SPACE : next comparison / swap
R     : reset with new random array
Q     : quit
"""

import argparse
import random
import sys

import pygame

# ── Visual constants ──────────────────────────────────────────────────────────
BG         = (13,  13,  13)
BAR_BASE   = (70,  80, 100)
BAR_CMP    = (247, 180,  60)   # amber   – just swapped
BAR_SWAP   = (124, 106, 247)   # purple  – being compared
BAR_SORTED = (52,  211, 153)   # green   – confirmed sorted
TEXT_COLOR = (226, 232, 240)
MUTED      = (100, 116, 139)
ACCENT     = (167, 139, 250)

FONT_SIZE   = 14
BAR_GAP     = 4
PADDING     = 48
BOTTOM_BAR  = 40
INFO_HEIGHT = 56


def build_steps(arr):
    """Pre-compute every (array_snapshot, i, j, swapped, sorted_indices) step."""
    a = arr[:]
    steps = []
    n = len(a)
    sorted_set = set()

    for i in range(n):
        for j in range(n - i - 1):
            # comparison step
            steps.append((a[:], j, j + 1, False, frozenset(sorted_set)))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                # swap step
                steps.append((a[:], j, j + 1, True, frozenset(sorted_set)))
        sorted_set.add(n - i - 1)

    # final state – everything sorted
    sorted_set = frozenset(range(n))
    steps.append((a[:], -1, -1, False, sorted_set))
    return steps


def draw_frame(screen, font, small_font, steps, step_idx, bar_w, bar_gap, max_val,
               win_w, win_h, n):
    screen.fill(BG)

    arr, ci, cj, swapped, sorted_set = steps[step_idx]

    bar_area_h = win_h - INFO_HEIGHT - BOTTOM_BAR - PADDING
    x_start = PADDING

    for idx, val in enumerate(arr):
        bar_h = int((val / max_val) * bar_area_h)
        x = x_start + idx * (bar_w + bar_gap)
        y = INFO_HEIGHT + PADDING + (bar_area_h - bar_h)

        if idx in sorted_set:
            color = BAR_SORTED
        elif idx == ci or idx == cj:
            color = BAR_SWAP if swapped else BAR_CMP
        else:
            color = BAR_BASE

        pygame.draw.rect(screen, color, (x, y, bar_w, bar_h), border_radius=3)

    # ── Info bar ──
    done = step_idx == len(steps) - 1
    comparisons = step_idx  # rough proxy
    current = "Swapped values" if swapped else f"Comparing indices {ci} and {cj}" if not done else "Array is fully sorted"
    status = "Sorted! Press R to reset." if done else f"Step {step_idx + 1} / {len(steps) - 1}"
    label = font.render(status, True, ACCENT if done else TEXT_COLOR)
    current_label = small_font.render(current, True, TEXT_COLOR)
    cmp_label = small_font.render(f"comparisons: {comparisons}", True, MUTED)
    size_label = small_font.render(f"n = {n}", True, MUTED)
    screen.blit(label, (PADDING, 16))
    screen.blit(cmp_label, (PADDING, 36))
    screen.blit(size_label, (win_w - PADDING - size_label.get_width(), 36))
    screen.blit(current_label, (PADDING, 42))

    # ── Bottom instruction bar ──
    instr = small_font.render("SPACE: next step   |   R: reset   |   Q: quit", True, MUTED)
    pygame.draw.line(screen, (30, 30, 30), (0, win_h - BOTTOM_BAR), (win_w, win_h - BOTTOM_BAR))
    screen.blit(instr, (win_w // 2 - instr.get_width() // 2, win_h - BOTTOM_BAR + 12))

    pygame.display.flip()


def main():
    parser = argparse.ArgumentParser(description="Trace — Bubble Sort Visualizer")
    parser.add_argument("--size", type=int, default=10,
                        help="Number of elements to sort (default: 10)")
    args = parser.parse_args()

    n = max(2, min(args.size, 60))

    pygame.init()
    pygame.display.set_caption("Trace — Bubble Sort")

    win_w, win_h = 900, 560
    screen = pygame.display.set_mode((win_w, win_h))

    font       = pygame.font.SysFont("monospace", FONT_SIZE + 2, bold=True)
    small_font = pygame.font.SysFont("monospace", FONT_SIZE - 1)

    def new_array():
        return random.sample(range(1, 101), min(n, 100))

    arr = new_array()
    steps = build_steps(arr)
    step_idx = 0
    max_val = max(arr)

    avail_w = win_w - 2 * PADDING
    bar_w = max(4, (avail_w - BAR_GAP * (n - 1)) // n)

    draw_frame(screen, font, small_font, steps, step_idx, bar_w, BAR_GAP,
               max_val, win_w, win_h, n)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()

                elif event.key == pygame.K_r:
                    arr = new_array()
                    steps = build_steps(arr)
                    step_idx = 0
                    max_val = max(arr)
                    bar_w = max(4, (avail_w - BAR_GAP * (n - 1)) // n)

                elif event.key == pygame.K_SPACE:
                    if step_idx < len(steps) - 1:
                        step_idx += 1

                draw_frame(screen, font, small_font, steps, step_idx, bar_w, BAR_GAP,
                           max_val, win_w, win_h, n)

        clock.tick(60)


if __name__ == "__main__":
    main()

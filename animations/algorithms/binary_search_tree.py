"""
Trace — Binary Search Tree Insertion Visualizer
SPACE : insert next value (animates traversal path first)
R     : reset and start over
Q     : quit
"""

import argparse
import sys
import time

import pygame

# ── Visual constants ──────────────────────────────────────────────────────────
BG           = (13,  13,  13)
NODE_DEFAULT = (35,  38,  50)
NODE_BORDER  = (70,  80, 100)
NODE_PATH    = (124, 106, 247)   # purple  – traversal highlight
NODE_NEW     = (52,  211, 153)   # green   – freshly inserted
NODE_HOVER   = (247, 180,  60)   # amber   – current compare
EDGE_COLOR   = (50,  55,  70)
TEXT_COLOR   = (226, 232, 240)
MUTED        = (100, 116, 139)
ACCENT       = (167, 139, 250)

FONT_SIZE    = 14
NODE_RADIUS  = 22
BOTTOM_BAR   = 40
INFO_HEIGHT  = 56

# How long the "new node" highlight lasts (seconds)
NEW_HIGHLIGHT_DUR = 1.2

# ms to highlight each node on the traversal path
TRAVERSAL_HIGHLIGHT_DUR = 5000   

class Node:
    def __init__(self, val):
        self.val   = val
        self.left  = None
        self.right = None


def insert(root, val):
    if root is None:
        return Node(val)
    if val < root.val:
        root.left  = insert(root.left,  val)
    else:
        root.right = insert(root.right, val)
    return root


def traversal_path(root, val):
    """Return list of node values visited on the way to where val would go."""
    path = []
    cur = root
    while cur:
        path.append(cur.val)
        if val < cur.val:
            cur = cur.left
        else:
            cur = cur.right
    return path


def assign_positions(root, depth=0, counter=None):
    """
    Assign (x_slot, depth) to each node in-order so nodes don't overlap.
    Returns dict: val -> (slot, depth)   -- not collision-safe for duplicates,
    but fine for the default value set and reasonable inputs.
    """
    if counter is None:
        counter = [0]
    if root is None:
        return {}
    pos = {}
    pos.update(assign_positions(root.left, depth + 1, counter))
    pos[root.val] = (counter[0], depth)
    counter[0] += 1
    pos.update(assign_positions(root.right, depth + 1, counter))
    return pos


def layout(root, win_w, win_h):
    """Return dict: node_val -> (px, py) pixel positions."""
    if root is None:
        return {}
    slots = assign_positions(root)
    n_slots = max(s for s, _ in slots.values()) + 1
    max_depth = max(d for _, d in slots.values())

    x_margin = 60
    y_margin = INFO_HEIGHT + 30
    usable_w = win_w - 2 * x_margin
    usable_h = win_h - y_margin - BOTTOM_BAR - 20

    x_step = usable_w / max(n_slots, 1)
    y_step = usable_h / max(max_depth, 1) if max_depth > 0 else usable_h

    positions = {}
    for val, (slot, depth) in slots.items():
        px = int(x_margin + slot * x_step + x_step / 2)
        py = int(y_margin + depth * y_step)
        positions[val] = (px, py)
    return positions


def draw_edges(screen, root, positions):
    if root is None:
        return
    if root.left:
        pygame.draw.line(screen, EDGE_COLOR,
                         positions[root.val], positions[root.left.val], 2)
        draw_edges(screen, root.left, positions)
    if root.right:
        pygame.draw.line(screen, EDGE_COLOR,
                         positions[root.val], positions[root.right.val], 2)
        draw_edges(screen, root.right, positions)


def draw_node(screen, font, pos, val, color, border):
    pygame.draw.circle(screen, color, pos, NODE_RADIUS)
    pygame.draw.circle(screen, border, pos, NODE_RADIUS, 2)
    label = font.render(str(val), True, TEXT_COLOR)
    screen.blit(label, (pos[0] - label.get_width() // 2,
                         pos[1] - label.get_height() // 2))


def draw_all_nodes(screen, font, root, positions, path_set, new_val, current_compare=None):
    if root is None:
        return
    if root.val == new_val:
        col, border = NODE_NEW, NODE_NEW
    elif root.val == current_compare:
        col, border = NODE_HOVER, NODE_HOVER          # amber — node being compared right now
    elif root.val in path_set:
        col, border = (70, 55, 140), ACCENT           # dimmer purple — already visited
    else:
        col, border = NODE_DEFAULT, NODE_BORDER
    draw_node(screen, font, positions[root.val], root.val, col, border)
    draw_all_nodes(screen, font, root.left,  positions, path_set, new_val, current_compare)
    draw_all_nodes(screen, font, root.right, positions, path_set, new_val, current_compare)


def render(screen, font, small_font, root, positions, path_set, new_val,
           info_text, win_w, win_h, compare_info=None, current_compare=None):
    screen.fill(BG)

    # Edges first (behind nodes)
    draw_edges(screen, root, positions)
    draw_all_nodes(screen, font, root, positions, path_set, new_val, current_compare)

    # Info bar — left
    label = font.render(info_text, True, ACCENT if "Done" in info_text else TEXT_COLOR)
    screen.blit(label, (20, 16))

    # ── Comparison panel (shown during traversal) ─────────────────────────────
    if compare_info:
        iv  = compare_info["insert_val"]
        nv  = compare_info["node_val"]
        sym = "<" if iv < nv else ">"
        direction = "left" if iv < nv else "right"
        arrow     = "◀  LEFT" if direction == "left" else "RIGHT  ▶"
        dir_color = (100, 180, 255) if direction == "left" else (255, 140, 80)

        panel_w, panel_h = 260, 86
        panel_x = win_w - panel_w - 20
        panel_y = 8

        # Background + border
        pygame.draw.rect(screen, (20, 20, 32),
                         (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(screen, NODE_PATH,
                         (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)

        # Accent strip on left edge
        pygame.draw.rect(screen, NODE_HOVER,
                         (panel_x, panel_y + 8, 3, panel_h - 16), border_radius=2)

        px, py = panel_x + 16, panel_y + 10

        # Row 1: inserting value
        lbl_ins = small_font.render("inserting", True, MUTED)
        val_ins = font.render(str(iv), True, NODE_NEW)
        screen.blit(lbl_ins, (px, py))
        screen.blit(val_ins, (px + 90, py - 1))

        # Row 2: current node
        lbl_node = small_font.render("node", True, MUTED)
        val_node  = font.render(str(nv), True, NODE_HOVER)
        screen.blit(lbl_node, (px, py + 22))
        screen.blit(val_node, (px + 90, py + 21))

        # Divider
        pygame.draw.line(screen, (40, 40, 55),
                         (panel_x + 12, py + 46), (panel_x + panel_w - 12, py + 46))

        # Row 3: comparison result + direction
        cmp_str  = f"{iv} {sym} {nv}"
        lbl_cmp  = font.render(cmp_str, True, TEXT_COLOR)
        lbl_dir  = font.render(arrow, True, dir_color)
        screen.blit(lbl_cmp, (px, py + 52))
        screen.blit(lbl_dir, (panel_x + panel_w - lbl_dir.get_width() - 14, py + 52))

    # Bottom bar
    instr = small_font.render("SPACE: next step   |   R: reset   |   Q: quit", True, MUTED)
    pygame.draw.line(screen, (30, 30, 30), (0, win_h - BOTTOM_BAR), (win_w, win_h - BOTTOM_BAR))
    screen.blit(instr, (win_w // 2 - instr.get_width() // 2, win_h - BOTTOM_BAR + 12))

    pygame.display.flip()


def animate_traversal(screen, font, small_font, root, positions, path,
                       insert_val, win_w, win_h):
    """Step through each node on the traversal path with a comparison panel."""
    for i, step_val in enumerate(path):
        past_path = set(path[:i])          # already-visited (dimmer purple)
        # current node (step_val) is highlighted amber via current_compare

        compare_info = {
            "insert_val": insert_val,
            "node_val":   step_val,
        }
        info = f"Inserting {insert_val}  —  step {i + 1}/{len(path)}"
        render(screen, font, small_font, root, positions, past_path, -1,
               info, win_w, win_h,
               compare_info=compare_info, current_compare=step_val)
        pygame.time.wait(TRAVERSAL_HIGHLIGHT_DUR)

        # pump events so window doesn't freeze
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit(); sys.exit()


def main():
    parser = argparse.ArgumentParser(description="Trace — BST Insertion Visualizer")
    parser.add_argument("--values", type=str, default="5,3,7,1,4,6,8",
                        help='Comma-separated values to insert (default: "5,3,7,1,4,6,8")')
    args = parser.parse_args()

    try:
        original_values = [int(v.strip()) for v in args.values.split(",") if v.strip()]
    except ValueError:
        print("Error: --values must be comma-separated integers.")
        sys.exit(1)

    pygame.init()
    pygame.display.set_caption("Trace — Binary Search Tree")

    win_w, win_h = 960, 600
    screen = pygame.display.set_mode((win_w, win_h))

    font       = pygame.font.SysFont("monospace", FONT_SIZE + 1, bold=True)
    small_font = pygame.font.SysFont("monospace", FONT_SIZE - 1)

    def reset():
        return None, list(original_values), 0, set(), -1, 0.0

    root, queue, inserted_count, path_set, new_val, new_highlight_t = reset()

    # Draw initial empty state
    info = f"Ready — {len(queue)} values to insert. Press SPACE."
    render(screen, font, small_font, root, {}, set(), -1, info, win_w, win_h)

    clock = pygame.time.Clock()

    while True:
        now = time.time()
        if new_val != -1 and (now - new_highlight_t) > NEW_HIGHLIGHT_DUR:
            # fade out the new-node highlight
            new_val = -1
            positions = layout(root, win_w, win_h)
            info_text = (f"Inserted {inserted_count}/{len(original_values)}"
                         + ("  — Done! Press R to reset." if not queue else "  — SPACE: insert next"))
            render(screen, font, small_font, root, positions, set(), new_val,
                   info_text, win_w, win_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()

                elif event.key == pygame.K_r:
                    root, queue, inserted_count, path_set, new_val, new_highlight_t = reset()
                    info = f"Reset — {len(queue)} values to insert. Press SPACE."
                    render(screen, font, small_font, root, {}, set(), -1, info, win_w, win_h)

                elif event.key == pygame.K_SPACE:
                    if queue:
                        val = queue.pop(0)
                        inserted_count += 1

                        # animate traversal
                        if root is not None:
                            path = traversal_path(root, val)
                            positions = layout(root, win_w, win_h)
                            animate_traversal(screen, font, small_font, root,
                                              positions, path, val, win_w, win_h)

                        # insert
                        root = insert(root, val)
                        positions = layout(root, win_w, win_h)
                        new_val = val
                        new_highlight_t = time.time()

                        remaining = len(queue)
                        info_text = (f"Inserted {val}  ({inserted_count}/{len(original_values)})"
                                     + ("  — Done! Press R to reset." if remaining == 0
                                        else f"  — {remaining} left"))
                        render(screen, font, small_font, root, positions, set(), new_val,
                               info_text, win_w, win_h)

        clock.tick(60)


if __name__ == "__main__":
    main()

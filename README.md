# Trace

> A local, interactive CS concept visualizer — step through algorithms and data structures one operation at a time.

## What is it?

**Trace** lets students and self-learners _see_ what's happening inside classic CS algorithms. Each concept is a standalone Pygame animation you can step through at your own pace with a keypress. Animations launch from a clean dark-themed web UI or directly from the terminal.

**Who is it for?**  
CS students, teaching assistants, and self-taught programmers who want intuition, not just pseudocode.

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-org/trace.git
cd trace

# 2. (Optional) create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Launch the Web UI

```bash
uvicorn server:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

- Pick a **course** from the landing page
- Click a **concept** to expand its parameter form
- Hit **▶ Run Animation** — a Pygame window opens immediately

---

## Run an Animation Directly (CLI)

Every animation is a standalone Python script. Run it directly:

```bash
# Bubble Sort — default 10 elements
python animations/data-structures/bubble_sort.py

# Bubble Sort — 25 elements
python animations/data-structures/bubble_sort.py --size 25

# BST — default values
python animations/algorithms/binary_search_tree.py

# BST — custom values
python animations/algorithms/binary_search_tree.py --values "10,5,15,3,7,12,18"
```

### Controls (all animations)

| Key     | Action                        |
|---------|-------------------------------|
| `SPACE` | Next step                     |
| `R`     | Reset with new / original data |
| `Q`     | Quit                          |

---

## Concepts Available

### 🗄️ Data Structures

| Concept      | Description                                          | Parameter  |
|--------------|------------------------------------------------------|------------|
| Bubble Sort  | Compare and swap adjacent elements step by step      | `--size N` |

### 🔭 Algorithms

| Concept                        | Description                                    | Parameter         |
|-------------------------------|------------------------------------------------|-------------------|
| Binary Search Tree Insertion  | Insert nodes one by one and trace the path     | `--values a,b,c`  |

---

## Tech Stack

| Layer      | Tech               |
|------------|--------------------|
| Animations | Python + Pygame    |
| Web UI     | FastAPI + Jinja2   |
| Server     | Uvicorn (ASGI)     |

---

## Contributing

Want to add a new concept? See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## License

MIT

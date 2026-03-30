> **Work in progress** - things will break and change often.

# Kaos Alpha

A visual trading strategy game. You build strategies by connecting nodes in a flow editor, then backtest them against synthetic instruments. Challenges and trading concepts evolve with each level.

Built with SvelteKit + FastAPI.

## Quick start

```bash
# install frontend deps
npm install

# install backend deps
cd backend && uv sync && cd ..

# run everything
npm run start
```

This boots up both the frontend (localhost:5173) and the backend (localhost:8000).

### Prerequisites

- Node.js
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

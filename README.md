# CampusBite

**A local campus lunch planner that asks: can I eat here and return before class?**

Proposed theme: Everyday AI. Intended track: Battlefield Lightning (lightweight computing).

## Prototype status — read first

This repository is a runnable **CPU-based, synthetic-data prototype**. It implements a small empirical dining-duration model, table-aware queue scheduling, and a deadline-aware lunch planner. It does **not** implement camera detection, neural-network inference, real restaurant feeds, map routing, a multi-restaurant cloud service, or ASUS UGen300 acceleration. Hardware deployment is planned, not demonstrated. No real-world accuracy or power/latency claims are made.

## Run locally

Install Python 3.10 or newer. No third-party packages, GPU, API keys, internet connection, or notebook are needed after downloading the repository.

Windows (VS Code terminal):

```powershell
py server.py
```

macOS / Linux:

```bash
python3 server.py
```

Open **http://127.0.0.1:8000**. Keep the terminal running. Stop with Ctrl+C. Run commands from the directory containing `server.py`. If `py` is unavailable but Python is installed, try `python server.py`. GitHub stores the source; GitHub Pages cannot run this Python backend.

## What you can demonstrate

1. Set departure and next-class time, group size, buffer and travel modes.
2. Compare three fictional restaurants using typical and cautious return times.
3. Expand table details to inspect occupied/free tables and residual dining estimates.
4. Change a table's occupancy or queue in Restaurant controls and recalculate.
5. Switch to a bicycle or tighten the deadline to show changing recommendations.
6. Reset the synthetic snapshot for a reproducible presentation.

The default departure is 12:00 and the class is 13:00. These are scenario inputs, not the wall clock. The same snapshot is assumed to apply at the chosen departure time. State changes are in memory and reset on server restart.

## Time accounting

`round trip = outbound travel + wait after arrival + dining session + return travel`

`margin = minutes until class - round trip - safety buffer`

Dining duration includes ordering, preparation, eating and payment **after seating**. Cleanup is charged before the next group can use the table. This avoids counting food preparation twice. Pre-seat ordering queues would need a separate model for a different restaurant workflow.

Distances for the outbound and return legs are separate, manually configured walking/cycling route lengths. Walking uses 80 m/min. Cycling uses 240 m/min plus 2 minutes per leg for unlocking/parking. They are demo assumptions, not map directions; the user supplies bike availability implicitly by choosing it.

## Local prediction model

`data/synthetic_meals.csv` contains 1,800 seeded synthetic completed dining sessions, grouped by meal category and party size. All rows carry `source=synthetic`. There are 100 samples for each meal-category/group-size combination.

For a party still seated after `e` minutes, retain historical durations `d > e`; estimate the median or 80th percentile of `d - e`. This is an empirical conditional duration estimator. It is lightweight statistical inference, not a trained vision network. For fewer than five surviving samples, an explicitly flagged heuristic returns 10 minutes (typical) or 20 minutes (cautious). Sparse-tail estimates are not reliable measurements.

The queue simulator schedules each waiting group to a suitable table. It respects table capacity, strict FIFO, cleanup, and repeated table turnover. Each group occupies one table; tables are not merged or shared. Existing queued groups arrive before departure time. The user joins on arrival. New arrivals between departure and arrival are not forecast, so waits may be underestimated in a real rush.

Typical and cautious scenarios use the median and 80th-percentile duration for each party respectively. **The cautious scenario is not an 80% bound or a calibrated on-time probability.** Quantiles cannot be added to obtain a joint confidence level. Routing can also change with table availability. Status is based on both scenario results: within budget if the cautious margin is nonnegative, tight if only the typical margin is nonnegative, otherwise likely late. Ranking uses the cautious round-trip total.

## Architecture

Current implementation runs browser UI → localhost HTTP server → local duration estimator and queue simulator. All three restaurants are simulated on one computer. There is no cloud transmission and no camera image collection in this version.

Proposed hardware phase: a restaurant-side camera feeds a compatible local person detector on the host + ASUS UGen300. Table-region occupancy and temporal tracking produce anonymous seating events. The host CPU runs the duration and queue model; only aggregate availability estimates would be sent to a student-facing service. Person detection alone cannot tell how much food remains or predict departure reliably. Seating timestamps, restaurant history and observed releases are required. Temporal smoothing and manual correction are also needed for occlusion and guests briefly leaving a table.

The vision model, accelerator SDK, model conversion, hardware performance, event transport and central service still need to be implemented and measured. Never present the planned hardware architecture as completed work.

## Repository contents

| File | Purpose |
|---|---|
| `server.py` | Local server, demo restaurant state, validated JSON API |
| `engine.py` | Conditional duration estimates, seating simulation, travel accounting |
| `static/` | English browser interface with no external scripts or fonts |
| `data/synthetic_meals.csv` | Reproducible synthetic dataset |
| `generate_data.py` | Rebuild synthetic dataset with seed 20261005 |
| `tests/test_engine.py` | Queue and prediction/accounting edge cases |
| `QUICKSTART_zh-TW.md` | Beginner-friendly setup and GitHub instructions |
| `DEMO.md` | Suggested demonstration sequence and submission checklist |

## Test and regenerate data

```bash
python -m unittest discover -s tests -v
python generate_data.py
```

Use `py` on Windows or `python3` on macOS/Linux if appropriate.

## API

- `GET /api/health`: model type and synthetic row count.
- `GET /api/state`: current synthetic tables and queue sizes.
- `POST /api/recommend`: `{ "party": 2, "buffer": 5, "now_min": 720, "class_min": 780, "out_mode": "walk", "back_mode": "walk" }`.
- `POST /api/update`: `{ "restaurant": "rice", "table": "A1", "party": 0, "elapsed": 0 }` or `{ "restaurant": "rice", "queue": [2, 1, 4] }`.
- `POST /api/reset`: `{}`.

POST bodies use `Content-Type: application/json`. The server binds to localhost and is intended for a single-user local demo. It has no user accounts or production persistence and should not be exposed to the public internet.

## Evaluation needed before field deployment

Collect consented, anonymized seating/departure observations from cooperating venues. Split evaluation by day or venue to prevent leakage. Compare residual-time and wait-time MAE against simple fixed-duration and average-duration baselines. Measure the rate of missed deadlines and recommendation coverage. On real hardware, measure person-detection quality, end-to-end latency, memory, power, and data sent upstream. Synthetic data cannot establish field accuracy or hardware efficiency.

## Academic and submission notes

This starter implementation was created with AI assistance. Review, understand, adapt, and accurately describe it in accordance with your course and competition policies. Record your own design decisions, experiments and changes. Do not claim synthetic examples are real deployments or that an unimplemented feature works. Add your actual team names/student IDs and repository/video links to the slides; do not put private credentials in the repository.

# FastAPI Background Job Worker Engine

An asynchronous background task processing engine built with FastAPI, implementing non-blocking I/O execution, idempotency checks, automated retry mechanisms, and job status tracking.

## 🚀 Key Features
* **Non-blocking Execution:** Instantly returns `HTTP 202 Accepted` with a unique `job_id` while executing heavy AI/Data tasks in the background.
* **Idempotency Protection:** Prevents duplicate processing or execution overlap for already processing/completed tasks.
* **Automated Retry Logic:** Retries failed tasks up to 3 times before setting the status to `FAILED`.
* **Job Status Polling:** Dedicated endpoint (`/api/status/{job_id}`) to query task state (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).

## 🛠️ Tech Stack
* **Framework:** FastAPI
* **Concurrency:** Python `asyncio`, `BackgroundTasks`
* **Data Standard:** UUID, JSON-compatible Job Storage

## 📌 API Endpoints
* `POST /api/generate` - Submits a heavy background task, returns `job_id`.
* `GET /api/status/{job_id}` - Checks current job status and execution result.

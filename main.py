# -*- coding: utf-8 -*-
import asyncio
import time
import uuid
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, status

app = FastAPI(title="Background Job Worker Engine")

# Job memory storage
jobs_db: Dict[str, Dict[str, Any]] = {}

async def simulate_ai_call(prompt: str) -> str:
    """Yavas calisan AI API cagrisini simule eder."""
    await asyncio.sleep(5)  # 5 saniyelik yapay gecikme
    return f"AI Yaniti: '{prompt}' ifadesi basariyla islendi."

async def run_background_job(job_id: str, prompt: str, max_retries: int = 3):
    """
    Arka planda calisan worker fonksiyonu.
    Idempotency, Retry ve Error Handling barindirir.
    """
    # 1. Idempotency Kontrolu
    if jobs_db[job_id]["status"] in ["COMPLETED", "PROCESSING"]:
        print(f"[{job_id}] Gorev zaten isleniyor veya bitti.")
        return

    jobs_db[job_id]["status"] = "PROCESSING"
    jobs_db[job_id]["updated_at"] = time.time()

    # 2. Retry Logic
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[{job_id}] Islem baslatildi (Deneme {attempt}/{max_retries})...")
            result = await simulate_ai_call(prompt)

            # Islem basarili
            jobs_db[job_id]["status"] = "COMPLETED"
            jobs_db[job_id]["result"] = result
            jobs_db[job_id]["updated_at"] = time.time()
            print(f"[{job_id}] Gorev basariyla tamamlandi.")
            return

        except Exception as e:
            print(f"[{job_id}] Hata olustu: {str(e)}")
            if attempt == max_retries:
                # 3. Alert / Error Handling
                jobs_db[job_id]["status"] = "FAILED"
                jobs_db[job_id]["error"] = f"Maksimum deneme sayisina ulasildi: {str(e)}"
                jobs_db[job_id]["updated_at"] = time.time()
                print(f"[{job_id}] Gorev tamamen basarisiz oldu.")
            else:
                await asyncio.sleep(2)

@app.post("/api/generate", status_code=status.HTTP_202_ACCEPTED)
async def create_task(prompt: str, background_tasks: BackgroundTasks):
    """
    Yavas islemi baslatir, aninda 202 Accepted ve job_id doner.
    """
    job_id = str(uuid.uuid4())

    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "PENDING",
        "result": None,
        "error": None,
        "created_at": time.time(),
        "updated_at": time.time()
    }

    background_tasks.add_task(run_background_job, job_id, prompt)

    return {
        "message": "Istek kabul edildi, arka planda isleniyor.",
        "job_id": job_id,
        "status_check_url": f"/api/status/{job_id}"
    }

@app.get("/api/status/{job_id}")
async def get_task_status(job_id: str):
    """
    Kullanicinin job_id ile gorevin durumunu sorguladigi endpoint.
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job ID bulunamadi.")
    
    return jobs_db[job_id]

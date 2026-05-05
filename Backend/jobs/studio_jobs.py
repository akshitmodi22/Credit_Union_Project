# ═══════════════════════════════════════════════════════════════
# jobs/studio_jobs.py — Watson Studio Job triggering
# ═══════════════════════════════════════════════════════════════

import time
import requests
from config import WATSONX_URL, WATSONX_KEY, PROJECT_ID, JOB_IDS


def get_iam_token() -> str:
    """Get IBM IAM token from API key."""
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type" : "urn:ibm:params:oauth:grant-type:apikey",
            "apikey"     : WATSONX_KEY
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]


def trigger_job(job_id: str) -> dict:
    """
    Triggers a Watson Studio Job using REST API directly.
    Polls every 10 seconds until complete or failed.
    """
    try:
        token   = get_iam_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type" : "application/json"
        }

        # ── Trigger job run ────────────────────────────────────
        run_url  = (
            f"https://api.dataplatform.cloud.ibm.com/v2/jobs/{job_id}/runs"
            f"?project_id={PROJECT_ID}&version=2023-07-07"
        )
        run_resp = requests.post(
            run_url,
            headers = headers,
            json    = {"job_run": {}}
        )
        print(f"status code : {run_resp.status_code}")
        print(f"Response    : {run_resp.text[:500]}")
        if run_resp.status_code not in [200, 201]:
            return {
                "state"  : "Error",
                "summary": f"Failed to start job: {run_resp.text}"
            }

        resp_json = run_resp.json()
        run_id    = resp_json["metadata"]["asset_id"]
        print(f"Job run started: {run_id}")

        # ── Poll for completion ────────────────────────────────
        status_url = (
            f"https://api.dataplatform.cloud.ibm.com/v2/jobs/{job_id}/runs/{run_id}"
            f"?project_id={PROJECT_ID}&version=2023-07-07"
        )

        for _ in range(60):   # max 10 minutes
            status_resp = requests.get(status_url, headers=headers)
            state       = (
                status_resp.json()
                .get("entity", {})
                .get("job_run", {})
                .get("state", "unknown")
            )
            print(f"Job state: {state}")

            if state == "Completed":
                return {
                    "state"  : "Completed",
                    "summary": "Job completed successfully"
                }
            elif state == "Failed":
                return {
                    "state"  : "Failed",
                    "summary": "Job failed in Watson Studio"
                }

            time.sleep(10)

        return {
            "state"  : "Timeout",
            "summary": "Job did not complete within 10 minutes"
        }

    except Exception as e:
        return {
            "state"  : "Error",
            "summary": str(e)
        }


def trigger_model_jobs(model: str, job_type: str) -> dict:
    """
    Triggers train or predict jobs for one or all models.

    model    : attrition / loan / propensity / all
    job_type : train / predict
    """
    key_map = {
        "attrition"  : f"attrition_{job_type}",
        "loan"       : f"loan_{job_type}",
        "propensity" : f"propensity_{job_type}"
    }

    models_to_run = (
        list(key_map.keys()) if model == "all" else [model]
    )

    results = {}
    for m in models_to_run:
        job_key = key_map.get(m)
        job_id  = JOB_IDS.get(job_key)

        if not job_id:
            results[m] = {
                "state"  : "Error",
                "summary": f"No job ID configured for {m} {job_type}"
            }
            continue

        results[m] = trigger_job(job_id)

    return results
# tests/lib/two_captcha_client.py
import os
import time
import typing as t
import requests

API_BASE = "https://api.2captcha.com"

class TwoCaptchaError(RuntimeError):
    pass

class TwoCaptchaClient:
    def __init__(self, api_key: t.Optional[str] = None, poll_interval: float = 3.0, timeout: float = 180.0):
        self.api_key = api_key or os.getenv("TWOCAPTCHA_API_KEY")
        if not self.api_key:
            raise TwoCaptchaError("TWOCAPTCHA_API_KEY not set")
        self.poll_interval = poll_interval
        self.timeout = timeout

    def get_balance(self) -> float:
        url = f"{API_BASE}/getBalance"
        resp = requests.post(url, json={"clientKey": self.api_key}, timeout=30)
        data = resp.json()
        if data.get("errorId"):
            raise TwoCaptchaError(f"getBalance error: {data}")
        # The API returns {"balance": "1.2345"} or with status fields
        bal = data.get("balance")
        try:
            return float(bal)
        except Exception as e:
            raise TwoCaptchaError(f"Unexpected balance payload: {data}") from e

    def create_task(self, task: dict) -> str:
        url = f"{API_BASE}/createTask"
        payload = {"clientKey": self.api_key, "task": task}
        resp = requests.post(url, json=payload, timeout=60)
        data = resp.json()
        if data.get("errorId"):
            raise TwoCaptchaError(f"createTask error: {data}")
        return data["taskId"]

    def get_task_result(self, task_id: str) -> dict:
        url = f"{API_BASE}/getTaskResult"
        payload = {"clientKey": self.api_key, "taskId": task_id}
        resp = requests.post(url, json=payload, timeout=60)
        data = resp.json()
        if data.get("errorId"):
            raise TwoCaptchaError(f"getTaskResult error: {data}")
        return data

    def solve(self, task: dict) -> dict:
        """Create task and poll until ready; returns the API 'solution' dict."""
        task_id = self.create_task(task)
        t0 = time.time()
        while True:
            data = self.get_task_result(task_id)
            if data.get("status") == "ready":
                return {"taskId": task_id, **data}
            if time.time() - t0 > self.timeout:
                raise TwoCaptchaError(f"Timeout waiting for task {task_id}: last={data}")
            time.sleep(self.poll_interval)

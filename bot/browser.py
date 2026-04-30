from __future__ import annotations
import json
from playwright.sync_api import sync_playwright, Browser, Page, Playwright


class BrowserClient:
    _instance: BrowserClient | None = None

    def __init__(self, headless: bool = False):
        self._playwright: Playwright = sync_playwright().start()
        self._browser: Browser = self._playwright.chromium.launch(headless=headless)
        self._page: Page = self._browser.new_page()

    @classmethod
    def get_instance(cls, headless: bool = False) -> BrowserClient:
        if cls._instance is None:
            cls._instance = cls(headless=headless)
        return cls._instance

    def navigate(self, url: str) -> str:
        try:
            self._page.goto(url, wait_until="networkidle", timeout=30000)
            return json.dumps({"success": True, "url": self._page.url, "title": self._page.title()})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_text(self, selector: str = "body") -> str:
        try:
            text = self._page.locator(selector).inner_text(timeout=10000)
            return json.dumps({"text": text[:3000]})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def click(self, selector: str) -> str:
        try:
            self._page.locator(selector).click(timeout=10000)
            self._page.wait_for_load_state("networkidle", timeout=15000)
            return json.dumps({"success": True, "current_url": self._page.url})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def fill(self, selector: str, value: str) -> str:
        try:
            self._page.locator(selector).fill(value, timeout=10000)
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def screenshot(self, path: str = "/tmp/screenshot.png") -> str:
        try:
            self._page.screenshot(path=path, full_page=False)
            return json.dumps({"success": True, "path": path})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def close(self) -> None:
        try:
            self._browser.close()
            self._playwright.stop()
        finally:
            BrowserClient._instance = None

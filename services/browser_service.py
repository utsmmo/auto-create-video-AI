from playwright.async_api import async_playwright
from services.gpm_service import GPMController
import os
import asyncio
import time
import uuid
import base64
import httpx
from typing import Dict, List

class BrowserService:
    def __init__(self):
        self.gpm = GPMController()
        self.playwright = None
        self.browser = None
        self.context = None
        self.output_dir = "static/outputs/images"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def start(self, profile_id: str, options: Dict = None) -> bool:
        if self.context: return True
        res = self.gpm.start_profile(profile_id, options=options)
        if not res.get("success"): return False
        ws_url = res.get("ws_url")
        if not ws_url: return False
        if not self.playwright: self.playwright = await async_playwright().start()
        try:
            self.browser = await self.playwright.chromium.connect_over_cdp(ws_url, timeout=60000)
            self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
            print("✅ Đã kết nối thành công với GPM Browser (Shared Context)!")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối Playwright: {str(e)}")
            return False

    async def generate_image(self, prompt: str, width: int = 1280, height: int = 720):
        if not self.context: return {"status": "error", "message": "GPM Browser chưa được khởi động."}
        page = await self.context.new_page()
        try:
            filename = f"gpm_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(self.output_dir, filename)
            from requests.utils import quote
            url = f"https://pollinations.ai/p/{quote(prompt)}?width={width}&height={height}&nologo=true"
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            await page.screenshot(path=file_path)
            return {"status": "success", "local_url": f"/static/outputs/images/{filename}", "file_path": file_path, "prompt": prompt}
        except Exception as e: return {"status": "error", "message": str(e)}
        finally: await page.close()

    async def generate_google_flow(self, prompt: str, project_url: str = None, gen_type: str = "image", 
                                aspect: str = "16:9", quantity: str = "x1", model: str = "Nano Banana 2"):
        if not self.context: return {"status": "error", "message": "GPM Browser chưa được khởi động."}
        page = await self.context.new_page()
        try:
            base_url = "https://labs.google/fx/tools/flow"
            if not project_url or project_url == base_url or "/project/" not in project_url:
                print(f"🆕 [SONG SONG] Đang tạo Project mới cho prompt: {prompt[:30]}...")
                await page.goto(base_url, wait_until="networkidle", timeout=60000)
                await page.wait_for_selector('button:has-text("New project")', timeout=20000)
                await page.click('button:has-text("New project")')
                await asyncio.sleep(5)
            else:
                print(f"🎬 [SONG SONG] Truy cập Project: {project_url}")
                await page.goto(project_url, wait_until="networkidle", timeout=60000)
                # Kiểm tra xem có bị redirect về trang chủ không (Project không tồn tại)
                if page.url == base_url or "/project/" not in page.url:
                    print("⚠️ Project không tồn tại, tạo mới...")
                    await page.click('button:has-text("New project")', timeout=10000)
                    await asyncio.sleep(5)
            
            # Cấu hình
            try:
                trigger = 'button:has-text("x1"), button:has-text("x2"), button:has-text("x3"), button:has-text("x4")'
                await page.wait_for_selector(trigger, timeout=10000)
                await page.click(trigger)
                await asyncio.sleep(1)
                await page.click('button:has-text("Image")' if gen_type == "image" else 'button:has-text("Video")')
                await page.click(f'button:has-text("{aspect}")')
                await page.click(f'button:has-text("{quantity}")')
                await page.keyboard.press("Escape")
            except: pass
            
            prompt_selector = 'div[role="textbox"]'
            await page.wait_for_selector(prompt_selector, timeout=20000)
            await page.click(prompt_selector)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.type(prompt)
            
            result_item_selector = 'div[scrollable="true"] a, .fZNDvE, a[href*="/project/"]'
            initial_count = len(await page.query_selector_all(result_item_selector))
            await page.keyboard.press("Enter")
            await asyncio.sleep(1)
            try: await page.eval_on_selector('button:has-text("Create")', "el => el.click()")
            except: pass

            qty_num = int(quantity.replace("x", ""))
            start_wait = time.time()
            new_items = []
            while time.time() - start_wait < 180:
                current_items = await page.query_selector_all(result_item_selector)
                if len(current_items) >= initial_count + qty_num:
                    new_items = current_items[initial_count : initial_count + qty_num]
                    break
                await asyncio.sleep(2)
            
            if not new_items: return {"status": "error", "message": "Timeout: Không thấy ảnh mới."}

            results = []
            for i, item in enumerate(new_items):
                item_done = False
                for _ in range(60):
                    text = await item.inner_text()
                    img = await item.query_selector("img")
                    if img and "%" not in text:
                        src = await img.get_attribute("src")
                        if src and "flower-placeholder" not in src:
                            media_url = src if src.startswith("http") else f"https://labs.google{src}"
                            b64 = None
                            try:
                                response = await page.request.get(media_url)
                                if response.ok: b64 = base64.b64encode(await response.body()).decode("utf-8")
                            except: pass
                            results.append({"url": media_url, "base64": b64})
                            item_done = True
                            break
                    await asyncio.sleep(2)
            
            # TRÍCH XUẤT PROJECT ID
            current_url = page.url
            final_project_id = None
            if "/project/" in current_url:
                final_project_id = current_url.split("/project/")[-1].split("?")[0]

            return {
                "status": "success", "images": results, "prompt": prompt, "aspect": aspect, 
                "quantity": quantity, "model": model, "project_id": final_project_id, 
                "project_url": current_url, "provider": "google_flow"
            }
        except Exception as e: return {"status": "error", "message": str(e)}
        finally: await page.close()

    async def stop(self, profile_id: str):
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
        self.gpm.stop_profile(profile_id)
        self.context = None

browser_service = BrowserService()

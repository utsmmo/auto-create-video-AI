"""
GPM Login Controller
Quản lý GPM Antidetect Browser thông qua Local API
"""

import requests
import time
from typing import Optional, Dict, Any, List


class GPMController:
    """
    Controller để giao tiếp với GPM Login Local API
    Mặc định chạy trên http://127.0.0.1:19995
    """
    
    def __init__(self, api_url: str = "http://127.0.0.1:19995"):
        self.api_url = api_url.rstrip("/")
        self.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Thực hiện request đến GPM API"""
        url = f"{self.api_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Method không hỗ trợ: {method}")
            
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Không thể kết nối GPM. Hãy chắc chắn GPM Login đang chạy!"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== PROFILE MANAGEMENT ====================
    
    def get_profiles(self, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """
        Lấy danh sách tất cả profile
        
        Returns:
            Dict với danh sách profiles và thông tin phân trang
        """
        return self._make_request("GET", f"/api/v3/profiles?page={page}&per_page={per_page}")
    
    def get_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết của một profile
        
        Args:
            profile_id: ID của profile
        """
        return self._make_request("GET", f"/api/v3/profiles/{profile_id}")
    
    def create_profile(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Tạo profile mới
        
        Args:
            name: Tên profile
            **kwargs: Các tùy chọn bổ sung như:
                - group_id: ID nhóm
                - raw_proxy: Proxy (vd: "socks5://user:pass@host:port")
                - startup_urls: Danh sách URL mở khi khởi động
                - note: Ghi chú
                
        Returns:
            Dict với thông tin profile vừa tạo
        """
        data = {
            "name": name,
            **kwargs
        }
        return self._make_request("POST", "/api/v3/profiles", data)
    
    def update_profile(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Cập nhật thông tin profile
        
        Args:
            profile_id: ID của profile
            **kwargs: Các trường cần cập nhật
        """
        return self._make_request("POST", f"/api/v3/profiles/{profile_id}", kwargs)
    
    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Xóa profile
        
        Args:
            profile_id: ID của profile cần xóa
        """
        return self._make_request("DELETE", f"/api/v3/profiles/{profile_id}")
    
    def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Đóng profile
        API: /api/v3/profiles/close/{profile_id}
        """
        return self._make_request("GET", f"/api/v3/profiles/close/{profile_id}")
    
    def start_profile(self, profile_id: str, options: Dict = None, automation: bool = True) -> Dict[str, Any]:
        """
        Khởi động profile browser với các tham số mở rộng theo tài liệu GPM
        """
        endpoint = f"/api/v3/profiles/start/{profile_id}"
        
        params = []
        if automation:
            params.append("automation=true")
        
        if options:
            for k, v in options.items():
                params.append(f"{k}={v}")
        
        if params:
            endpoint = f"{endpoint}?{'&'.join(params)}"
        
        print(f"[GPM] Mở profile: {profile_id}...")
        result = self._make_request("GET", endpoint)
        
        if result.get("success") and "data" in result:
            data = result["data"]
            debugging_address = data.get("remote_debugging_address")
            
            # Ưu tiên lấy ws_url trả về trực tiếp
            ws_url = data.get("ws_url") or data.get("browser_wsEndpoint") or data.get("browserWSEndpoint")
            
            # Nếu không có ws_url, xây dựng từ debugging_address
            if not ws_url and debugging_address:
                # Playwright có thể connect trực tiếp qua http endpoint
                ws_url = f"http://{debugging_address}"
                
            return {
                "success": True,
                "ws_url": ws_url,
                "remote_debugging": debugging_address,
                "data": data
            }
        
        return {"success": False, "message": result.get("message", "Unknown error")}
    def close_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Đóng profile browser đang chạy
        
        Args:
            profile_id: ID của profile
        """
        return self._make_request("GET", f"/api/v3/profiles/close/{profile_id}")
    
    def close_all_profiles(self) -> List[Dict[str, Any]]:
        """Đóng tất cả profile đang chạy"""
        return self._make_request("GET", "/api/v3/profiles/close-all")

    def get_groups(self) -> Dict[str, Any]:
        """
        Lấy danh sách nhóm từ GPM API
        Endpoint: GET /api/v3/groups
        
        Returns:
            Dict với data là list các nhóm, mỗi nhóm có: id, name, sort, ...
        """
        return self._make_request("GET", "/api/v3/groups")
    
    # ==================== UTILITY METHODS ====================
    
    def check_connection(self) -> bool:
        """
        Kiểm tra kết nối đến GPM API
        
        Returns:
            True nếu kết nối thành công
        """
        result = self._make_request("GET", "/api/v3/profiles?page=1&per_page=1")
        return result.get("success", False) or "data" in result
    
    def get_running_profiles(self) -> List[Dict]:
        """Lấy danh sách các profile đang chạy"""
        result = self.get_profiles()
        if result.get("success") and result.get("data"):
            return [p for p in result["data"]["profiles"] if p.get("status") == "running"]
        return []
    
    def wait_for_profile_ready(self, profile_id: str, timeout: int = 30) -> bool:
        """
        Chờ profile sẵn sàng sau khi khởi động
        
        Args:
            profile_id: ID của profile
            timeout: Timeout tính bằng giây
            
        Returns:
            True nếu profile đã sẵn sàng
        """
        start = time.time()
        while time.time() - start < timeout:
            result = self.get_profile_by_id(profile_id)
            if result.get("data", {}).get("status") == "running":
                return True
            time.sleep(1)
        return False


# ==================== QUICK TEST ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 GPM Controller Test")
    print("=" * 50)
    
    gpm = GPMController()
    
    # Test kết nối
    print("\n📡 Kiểm tra kết nối GPM...")
    if gpm.check_connection():
        print("✅ Kết nối GPM thành công!")
        
        # Lấy danh sách profiles
        profiles = gpm.get_profiles()
        if profiles.get("success") or profiles.get("data"):
            profile_list = profiles.get("data", {}).get("profiles", [])
            print(f"\n📋 Tìm thấy {len(profile_list)} profile(s)")
            for p in profile_list[:5]:  # Hiển thị tối đa 5 profile
                print(f"   - {p.get('name')} (ID: {p.get('id')})")
        else:
            print(f"⚠️ Không lấy được danh sách: {profiles}")
    else:
        print("❌ Không thể kết nối GPM!")
        print("   → Hãy chắc chắn GPM Login đang chạy")
        print("   → Kiểm tra cổng API trong GPM Settings")

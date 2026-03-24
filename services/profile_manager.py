import os
import json

class ProfileManager:
    def __init__(self, config_path="accounts.json"):
        self.config_path = config_path
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return [
            {"profile_id": "Profile1", "credits": 50, "status": "active"},
            {"profile_id": "Profile2", "credits": 50, "status": "active"}
        ]

    def save_accounts(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=4)

    def get_available_profile(self):
        """Lấy profile đầu tiên còn credit"""
        for acc in self.accounts:
            if acc.get("credits", 0) > 0 and acc.get("status") == "active":
                return acc
        return None

    def deduct_credit(self, profile_id: str, amount: int = 1):
        """Trừ credit sau khi dùng"""
        for acc in self.accounts:
            if acc["profile_id"] == profile_id:
                acc["credits"] = max(0, acc["credits"] - amount)
                if acc["credits"] == 0:
                    acc["status"] = "exhausted"
                self.save_accounts()
                return True
        return False

profile_manager = ProfileManager()

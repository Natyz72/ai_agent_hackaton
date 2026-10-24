from typing import Any

from app.config import settings


class SupabaseClient:
    def __init__(self):
        self.url = settings.supabase_url
        self.key = settings.supabase_service_role_key
        self._client = None

    def get_client(self):
        if self._client is not None:
            return self._client
        if not self.url or not self.key:
            return None
        try:
            from supabase import create_client

            self._client = create_client(self.url, self.key)
            return self._client
        except Exception:
            return None


db_client = SupabaseClient()

import os
import logging
import requests
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XSignAlert:
    def __init__(self):
        self.api_key = os.getenv('X_SIGN_API_KEY')
        self.channel_id = os.getenv('X_SIGN_CHANNEL_ID')
        self.base_url = 'https://api.x-sign.io/v1'

    def send_alert(self, title: str, message: str, tags: List[str] | None = None):
        """
        Send an alert to x-sign
        """
        if not self.api_key or not self.channel_id:
            # Alerting not configured
            return False
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'channel_id': self.channel_id,
                'title': title,
                'message': message,
                'tags': tags or ['solana', 'bundler']
            }
            resp = requests.post(f"{self.base_url}/messages", json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            logger.info("Alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False

    def send_transaction_alert(self, tx_hash: str, status: str, bundle_size: int):
        """
        Send transaction-specific alert
        """
        tags = ['transaction', f'status_{status.lower()}']
        message = f"Transaction {tx_hash[:8]}...{tx_hash[-8:]} {status}"
        if bundle_size:
            message += f" (Bundle size: {bundle_size} txs)"
            tags.append('bundle')
        
        self.send_alert(
            title=f"Transaction {status}",
            message=message,
            tags=tags
        )

    def send_error_alert(self, error_type: str, details: str):
        """
        Send error alert
        """
        self.send_alert(
            title=f"Error: {error_type}",
            message=details,
            tags=['error', error_type.lower()]
        )

import os
import json
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Initialize logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class WalletAgingSystem:
    def __init__(self):
        """Initialize the wallet aging system"""
        self.wallets_file = os.getenv('WALLETS_FILE', 'wallets.json')
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.min_age = int(os.getenv('MIN_WALLET_AGE', 24))  # hours
        self.max_age = int(os.getenv('MAX_WALLET_AGE', 168))  # hours
        self.wallets = {}
        self._load_wallets()

    def _load_wallets(self):
        """Load wallets from file"""
        try:
            if os.path.exists(self.wallets_file):
                with open(self.wallets_file, 'r') as f:
                    encrypted_data = f.read()
                    fernet = Fernet(self.encryption_key.encode())
                    decrypted_data = fernet.decrypt(encrypted_data.encode())
                    self.wallets = json.loads(decrypted_data.decode())
            else:
                self.wallets = {}
        except Exception as e:
            logger.error(f"Failed to load wallets: {str(e)}")
            self.wallets = {}

    def _save_wallets(self):
        """Save wallets to file"""
        try:
            fernet = Fernet(self.encryption_key.encode())
            encrypted_data = fernet.encrypt(json.dumps(self.wallets).encode())
            with open(self.wallets_file, 'w') as f:
                f.write(encrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to save wallets: {str(e)}")

    def create_wallet(self, private_key: str) -> str:
        """Create a new wallet"""
        try:
            wallet_id = f"wallet_{len(self.wallets) + 1}"
            self.wallets[wallet_id] = {
                'private_key': private_key,
                'created_at': datetime.utcnow().isoformat(),
                'last_used': None,
                'transaction_count': 0
            }
            self._save_wallets()
            return wallet_id
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            return None

    def get_wallet(self) -> str:
        """Get an available wallet"""
        current_time = datetime.utcnow()
        
        # Find an available wallet
        for wallet_id, wallet in self.wallets.items():
            created_at = datetime.fromisoformat(wallet['created_at'])
            last_used = wallet['last_used']
            if last_used:
                last_used = datetime.fromisoformat(last_used)
            
            # Check wallet age
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            # Check if wallet is available
            if self.min_age <= age_hours <= self.max_age:
                # Check if wallet is not recently used
                if not last_used or (current_time - last_used).total_seconds() > 3600:  # 1 hour cooldown
                    wallet['last_used'] = current_time.isoformat()
                    wallet['transaction_count'] += 1
                    self._save_wallets()
                    return wallet_id
        
        return None

    def retire_wallet(self, wallet_id: str) -> bool:
        """Retire a wallet"""
        if wallet_id in self.wallets:
            del self.wallets[wallet_id]
            self._save_wallets()
            return True
        return False

    def get_wallet_stats(self) -> dict:
        """Get wallet statistics"""
        current_time = datetime.utcnow()
        
        stats = {
            'total_wallets': len(self.wallets),
            'new_wallets': 0,
            'active_wallets': 0,
            'retired_wallets': 0,
            'total_transactions': 0
        }
        
        for wallet in self.wallets.values():
            created_at = datetime.fromisoformat(wallet['created_at'])
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            if age_hours < self.min_age:
                stats['new_wallets'] += 1
            elif age_hours <= self.max_age:
                stats['active_wallets'] += 1
            else:
                stats['retired_wallets'] += 1
                
            stats['total_transactions'] += wallet['transaction_count']
        
        return stats

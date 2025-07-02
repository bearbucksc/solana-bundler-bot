from datetime import datetime

class Wallet:
    def __init__(self, address, created_at, last_used=None):
        self.address = address
        self.created_at = created_at
        self.last_used = last_used
        self.transaction_count = 0

    def __repr__(self):
        return f"<Wallet {self.address[:8]}...>"

    def to_dict(self):
        return {
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'transaction_count': self.transaction_count
        }

    def update_last_used(self):
        self.last_used = datetime.utcnow()
        self.transaction_count += 1

    def is_active(self, min_age, max_age):
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return min_age <= age_hours <= max_age

    def is_retired(self, max_age):
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return age_hours >= max_age

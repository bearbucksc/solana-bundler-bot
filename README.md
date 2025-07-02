# Solana Bundler Bot

A sophisticated bundler bot for Solana network that provides atomic transaction execution using Jito, multi-wallet management, and real-time monitoring.

## Features

- Jito bundle integration for atomic transaction execution
- Multi-wallet management with aging system
- Real-time monitoring dashboard
- X-sign alert integration
- MEV protection and anti-frontrunning
- Volume generation engine
- Token launch support
- Analytics and logging
- Secure encrypted key storage

## Prerequisites

- Python 3.8+
- Docker (optional)
- Solana CLI
- x-sign account for alerts

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solana-bundler-bot.git
cd solana-bundler-bot
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration:
- Set your encryption key
- Configure RPC endpoints
- Add your x-sign API key and channel ID
- Set other configuration parameters

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Generate encryption key (if not provided):
```bash
python -c "import os; print(os.urandom(32).hex())" > encryption_key.txt
```

## Running the Application

### Without Docker
```bash
python app.py
```

### With Docker
```bash
docker build -t solana-bundler-bot .
docker run -d -p 5000:5000 -p 8765:8765 -v $(pwd)/wallets.json:/app/wallets.json solana-bundler-bot
```

## Accessing the Dashboard

Open your browser and navigate to:
```
http://localhost:5000
```

## Security Features

- All private keys are encrypted using Fernet
- Rate limiting protection
- MEV protection with configurable priority fees
- Secure wallet management
- Environment-based configuration

## Monitoring

The dashboard provides real-time monitoring of:
- Wallet statistics
- Bundle creation
- Transaction status
- System health
- Analytics data

## Alert Integration

The bot integrates with x-sign for:
- Transaction alerts
- Error notifications
- System status updates
- Custom alerts

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this code in your projects

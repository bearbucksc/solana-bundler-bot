from flask import render_template, jsonify, request
from webapp import socketio
from webapp.app import bp
from webapp.utils.wallet_aging import WalletAgingSystem
from webapp.utils.alert import XSignAlert
import os
import logging
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from datetime import datetime

# Initialize components
wallet_system = WalletAgingSystem()
x_alert = XSignAlert()

# Logging setup
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/wallets')
def get_wallets():
    """Get wallet statistics and list"""
    stats = wallet_system.get_wallet_stats()
    return jsonify(stats)

@bp.route('/api/bundle', methods=['POST'])
def create_bundle():
    """Create and execute a bundle"""
    try:
        data = request.json
        if not data or 'transactions' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        wallet = wallet_system.get_wallet()
        if not wallet:
            return jsonify({'error': 'No available wallets'}), 400

        # Validate transactions
        if not isinstance(data['transactions'], list):
            return jsonify({'error': 'Transactions must be a list'}), 400

        # Initialize Solana client
        client = Client(os.getenv('RPC_URL'))
        
        # Create transaction
        tx = Transaction().add(*data['transactions'])
        
        # Sign and send transaction
        try:
            signature = client.send_transaction(
                tx,
                wallet,
                opts=TxOpts(
                    skip_confirmation=False,
                    max_retries=5,
                    preflight_commitment=Confirmed,
                    priority_fee=int(os.getenv('MIN_PRIORITY_FEE'))
                )
            )
            
            result = {
                'signature': signature['result'],
                'success': True
            }
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            result = {
                'error': str(e),
                'success': False
            }

        # Send alert
        x_alert.send_transaction_alert(
            tx_hash=result.get('signature', ''),
            status='Success' if result.get('success', False) else 'Failed',
            bundle_size=len(data['transactions'])
        )

        # Emit bundle created event
        socketio.emit('bundle_created', {
            'signature': result.get('signature', ''),
            'success': result.get('success', False),
            'timestamp': datetime.utcnow().isoformat()
        })

        return jsonify(result)
    except ValueError as ve:
        logger.error(f"JSON validation error: {str(ve)}")
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        logger.error(f"Bundle creation failed: {str(e)}")
        x_alert.send_error_alert('Bundle', str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    socketio.emit('status', {'status': 'connected'})
    # Send initial analytics
    stats = wallet_system.get_wallet_stats()
    socketio.emit('analytics', stats)

# Background task for analytics
def analytics_task():
    while True:
        try:
            stats = wallet_system.get_wallet_stats()
            socketio.emit('analytics', stats)
            socketio.sleep(int(os.getenv('ANALYTICS_INTERVAL', 300)))
        except Exception as e:
            logger.error(f"Analytics task failed: {str(e)}")
            socketio.sleep(60)  # Wait before retrying

if __name__ == '__main__':
    socketio.start_background_task(analytics_task)

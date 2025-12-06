"""
Guardian Node REST API Server
Provides mobile app integration, remote control, and smart home capabilities
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import threading
import time
import hashlib
import secrets
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# --- Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app access
logger = logging.getLogger('guardian_api')
logger.setLevel(logging.INFO)

# Global state
SYSTEM_ONLINE_MODE = False
guardian_cli_instance = None
override_password_hash = None
password_usage_log = []

# Configuration paths
CONFIG_DIR = Path('data/config')
PASSWORD_FILE = CONFIG_DIR / 'override_password.json'
NOTIFICATION_CONFIG = CONFIG_DIR / 'notifications.json'

# Ensure config directory exists (will be created when server starts)
def ensure_config_dir():
    """Ensure config directory exists"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create config directory: {e}")


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================

def load_override_password():
    """Load override password from secure storage"""
    global override_password_hash
    try:
        if PASSWORD_FILE.exists():
            with open(PASSWORD_FILE, 'r') as f:
                data = json.load(f)
                override_password_hash = data.get('password_hash')
                logger.info("✅ Override password loaded")
        else:
            # Generate default password on first run
            default_password = secrets.token_urlsafe(12)
            save_override_password(default_password)
            logger.warning(f"⚠️ Generated default override password: {default_password}")
            logger.warning("⚠️ Change this immediately via /api/password/set")
    except Exception as e:
        logger.error(f"Failed to load override password: {e}")


def save_override_password(password: str):
    """Save override password securely"""
    global override_password_hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    override_password_hash = password_hash
    
    data = {
        'password_hash': password_hash,
        'created_at': datetime.now().isoformat(),
        'secret_from_kids': True  # Password should be secret from children
    }
    
    with open(PASSWORD_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info("✅ Override password saved securely")


def verify_override_password(password: str) -> bool:
    """Verify override password"""
    if not override_password_hash:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == override_password_hash


def log_password_usage(success: bool, source: str = "unknown"):
    """Log password usage attempts"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'source': source,
        'ip': request.remote_addr if request else 'local'
    }
    
    password_usage_log.append(entry)
    
    # Keep only last 100 entries
    if len(password_usage_log) > 100:
        password_usage_log.pop(0)
    
    # Send notification if password was used
    if success:
        send_notification(
            title="Override Password Used",
            message=f"Override password was used from {source} at {entry['timestamp']}",
            priority="high"
        )
    
    logger.info(f"Password usage: success={success}, source={source}")


# ============================================================================
# NOTIFICATION SYSTEM
# ============================================================================

def load_notification_config() -> Dict[str, Any]:
    """Load notification configuration"""
    try:
        if NOTIFICATION_CONFIG.exists():
            with open(NOTIFICATION_CONFIG, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load notification config: {e}")
    
    # Default configuration
    return {
        'enabled': True,
        'methods': {
            'log': True,  # Always log
            'pushover': False,  # Requires API key
            'email': False,  # Requires SMTP config
            'webhook': False  # Requires webhook URL
        },
        'pushover': {
            'user_key': '',
            'api_token': ''
        },
        'email': {
            'smtp_server': '',
            'smtp_port': 587,
            'username': '',
            'password': '',
            'to_address': ''
        },
        'webhook': {
            'url': ''
        }
    }


def send_notification(title: str, message: str, priority: str = "normal"):
    """Send notification via configured methods"""
    config = load_notification_config()
    
    if not config.get('enabled', True):
        return
    
    # Always log
    logger.info(f"📢 NOTIFICATION: {title} - {message}")
    
    # Pushover (mobile push notifications)
    if config['methods'].get('pushover'):
        try:
            import requests
            pushover_config = config.get('pushover', {})
            if pushover_config.get('user_key') and pushover_config.get('api_token'):
                requests.post('https://api.pushover.net/1/messages.json', data={
                    'token': pushover_config['api_token'],
                    'user': pushover_config['user_key'],
                    'title': title,
                    'message': message,
                    'priority': 1 if priority == 'high' else 0
                })
                logger.info("✅ Pushover notification sent")
        except Exception as e:
            logger.error(f"Failed to send Pushover notification: {e}")
    
    # Email notifications
    if config['methods'].get('email'):
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            email_config = config.get('email', {})
            if email_config.get('smtp_server') and email_config.get('to_address'):
                msg = MIMEText(message)
                msg['Subject'] = f"Guardian Node: {title}"
                msg['From'] = email_config['username']
                msg['To'] = email_config['to_address']
                
                with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(email_config['username'], email_config['password'])
                    server.send_message(msg)
                
                logger.info("✅ Email notification sent")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    # Webhook notifications
    if config['methods'].get('webhook'):
        try:
            import requests
            webhook_config = config.get('webhook', {})
            if webhook_config.get('url'):
                requests.post(webhook_config['url'], json={
                    'title': title,
                    'message': message,
                    'priority': priority,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Webhook notification sent")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")


# ============================================================================
# API ROUTES - SYSTEM STATUS
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current system status"""
    status = {
        "system_status": "Operational",
        "llm_loaded": guardian_cli_instance.llm is not None if guardian_cli_instance else False,
        "online_mode": SYSTEM_ONLINE_MODE,
        "api_port": 5000,
        "current_time": time.ctime(),
        "features": {
            "memory_vault": guardian_cli_instance.memory_vault is not None if guardian_cli_instance else False,
            "network_scanner": guardian_cli_instance.network_scanner is not None if guardian_cli_instance else False,
            "voice_interface": guardian_cli_instance.voice_interface is not None if guardian_cli_instance else False
        }
    }
    return jsonify(status), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "timestamp": time.time()}), 200


# ============================================================================
# API ROUTES - ONLINE MODE CONTROL
# ============================================================================

@app.route('/api/online_mode', methods=['GET'])
def get_online_mode():
    """Get current online mode status"""
    return jsonify({"online_mode": SYSTEM_ONLINE_MODE}), 200


@app.route('/api/online_mode', methods=['POST'])
def set_online_mode():
    """Set online mode (requires authentication)"""
    data = request.get_json()
    new_state = data.get('state')
    password = data.get('password')
    
    # Verify password
    if not verify_override_password(password):
        log_password_usage(False, "online_mode_change")
        return jsonify({"error": "Invalid password"}), 401
    
    log_password_usage(True, "online_mode_change")
    
    global SYSTEM_ONLINE_MODE
    SYSTEM_ONLINE_MODE = new_state
    
    if guardian_cli_instance:
        guardian_cli_instance.set_online_mode(new_state)
    
    logger.info(f"API set online mode to: {SYSTEM_ONLINE_MODE}")
    return jsonify({"success": True, "online_mode": SYSTEM_ONLINE_MODE}), 200


# ============================================================================
# API ROUTES - PASSWORD MANAGEMENT
# ============================================================================

@app.route('/api/password/set', methods=['POST'])
def set_password():
    """Set new override password (requires old password)"""
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"error": "Both old_password and new_password required"}), 400
    
    # Verify old password
    if not verify_override_password(old_password):
        log_password_usage(False, "password_change")
        return jsonify({"error": "Invalid old password"}), 401
    
    # Save new password
    save_override_password(new_password)
    log_password_usage(True, "password_change")
    
    return jsonify({"success": True, "message": "Password updated successfully"}), 200


@app.route('/api/password/verify', methods=['POST'])
def verify_password():
    """Verify override password"""
    data = request.get_json()
    password = data.get('password')
    
    if verify_override_password(password):
        log_password_usage(True, "password_verify")
        return jsonify({"valid": True}), 200
    else:
        log_password_usage(False, "password_verify")
        return jsonify({"valid": False}), 200


@app.route('/api/password/usage', methods=['GET'])
def get_password_usage():
    """Get password usage log (requires authentication)"""
    password = request.args.get('password')
    
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    return jsonify({"usage_log": password_usage_log}), 200


# ============================================================================
# API ROUTES - LLM QUERIES
# ============================================================================

@app.route('/api/query', methods=['POST'])
def handle_llm_query():
    """Process LLM query"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    if not guardian_cli_instance or not guardian_cli_instance.llm:
        return jsonify({"error": "LLM not available"}), 503
    
    try:
        # Capture response
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        guardian_cli_instance.run_query(query)
        
        output = buffer.getvalue()
        sys.stdout = old_stdout
        
        return jsonify({
            "success": True,
            "query": query,
            "response": output,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ROUTES - MEMORY VAULT
# ============================================================================

@app.route('/api/memory/stats', methods=['GET'])
def get_memory_stats():
    """Get memory vault statistics"""
    if not guardian_cli_instance or not guardian_cli_instance.memory_vault:
        return jsonify({"error": "Memory vault not available"}), 503
    
    stats = guardian_cli_instance.memory_vault.get_stats()
    return jsonify(stats), 200


@app.route('/api/memory/search', methods=['POST'])
def search_memory():
    """Search memory vault"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    if not guardian_cli_instance or not guardian_cli_instance.memory_vault:
        return jsonify({"error": "Memory vault not available"}), 503
    
    results = guardian_cli_instance.memory_vault.retrieve_relevant_memories(query)
    return jsonify({"results": results}), 200


# ============================================================================
# API ROUTES - NETWORK SCANNING
# ============================================================================

@app.route('/api/scan/network', methods=['POST'])
def scan_network():
    """Scan local network for devices"""
    data = request.get_json()
    network_range = data.get('network_range', '192.168.1.0/24')
    password = data.get('password')
    
    # Require password for network scanning
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    if not guardian_cli_instance or not guardian_cli_instance.network_scanner:
        return jsonify({"error": "Network scanner not available"}), 503
    
    try:
        devices = guardian_cli_instance.network_scanner.discover_local_network(network_range)
        return jsonify({
            "success": True,
            "devices": devices,
            "count": len(devices)
        }), 200
    except Exception as e:
        logger.error(f"Network scan error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ROUTES - NOTIFICATIONS
# ============================================================================

@app.route('/api/notifications/config', methods=['GET'])
def get_notification_config():
    """Get notification configuration"""
    config = load_notification_config()
    # Remove sensitive data
    if 'pushover' in config:
        config['pushover'] = {'configured': bool(config['pushover'].get('user_key'))}
    if 'email' in config:
        config['email'] = {'configured': bool(config['email'].get('smtp_server'))}
    
    return jsonify(config), 200


@app.route('/api/notifications/config', methods=['POST'])
def set_notification_config():
    """Update notification configuration (requires password)"""
    data = request.get_json()
    password = data.get('password')
    
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    config = data.get('config')
    if not config:
        return jsonify({"error": "Config required"}), 400
    
    try:
        with open(NOTIFICATION_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({"success": True, "message": "Notification config updated"}), 200
    except Exception as e:
        logger.error(f"Failed to save notification config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/notifications/test', methods=['POST'])
def test_notification():
    """Send test notification"""
    data = request.get_json()
    password = data.get('password')
    
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    send_notification(
        title="Test Notification",
        message="This is a test notification from Guardian Node",
        priority="normal"
    )
    
    return jsonify({"success": True, "message": "Test notification sent"}), 200


# ============================================================================
# API ROUTES - NODDY CONTROL FLOW
# ============================================================================

# Store for pending permission requests (for mobile app)
pending_permissions = {}

@app.route('/api/noddy/check_query', methods=['POST'])
def check_query_needs_internet():
    """Check if a query needs internet access"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    if not guardian_cli_instance:
        return jsonify({"error": "Guardian not available"}), 503
    
    needs_internet = guardian_cli_instance.needs_internet(query)
    
    return jsonify({
        "query": query,
        "needs_internet": needs_internet,
        "current_online_mode": guardian_cli_instance.online_mode
    }), 200


@app.route('/api/noddy/request_permission', methods=['POST'])
def request_online_permission():
    """Request permission to go online (for mobile app)"""
    data = request.get_json()
    query = data.get('query')
    request_id = data.get('request_id', str(time.time()))
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    # Store pending request
    pending_permissions[request_id] = {
        'query': query,
        'status': 'pending',
        'timestamp': time.time()
    }
    
    return jsonify({
        "request_id": request_id,
        "status": "pending",
        "message": "Permission request created. User needs to approve."
    }), 200


@app.route('/api/noddy/permission_status/<request_id>', methods=['GET'])
def get_permission_status(request_id):
    """Get status of permission request"""
    if request_id not in pending_permissions:
        return jsonify({"error": "Request not found"}), 404
    
    return jsonify(pending_permissions[request_id]), 200


@app.route('/api/noddy/grant_permission/<request_id>', methods=['POST'])
def grant_permission(request_id):
    """Grant permission for online access (requires password)"""
    data = request.get_json()
    password = data.get('password')
    
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    if request_id not in pending_permissions:
        return jsonify({"error": "Request not found"}), 404
    
    pending_permissions[request_id]['status'] = 'granted'
    pending_permissions[request_id]['granted_at'] = time.time()
    
    # Set online mode
    if guardian_cli_instance:
        guardian_cli_instance.set_online_mode(True)
    
    return jsonify({
        "request_id": request_id,
        "status": "granted",
        "message": "Permission granted. System is now online."
    }), 200


@app.route('/api/noddy/deny_permission/<request_id>', methods=['POST'])
def deny_permission(request_id):
    """Deny permission for online access (requires password)"""
    data = request.get_json()
    password = data.get('password')
    
    if not verify_override_password(password):
        return jsonify({"error": "Invalid password"}), 401
    
    if request_id not in pending_permissions:
        return jsonify({"error": "Request not found"}), 404
    
    pending_permissions[request_id]['status'] = 'denied'
    pending_permissions[request_id]['denied_at'] = time.time()
    
    return jsonify({
        "request_id": request_id,
        "status": "denied",
        "message": "Permission denied. System remains offline."
    }), 200


# ============================================================================
# API ROUTES - SMART HOME CONTROL (PLACEHOLDER)
# ============================================================================

@app.route('/api/smarthome/devices', methods=['GET'])
def list_smart_devices():
    """List available smart home devices"""
    if not guardian_cli_instance or not guardian_cli_instance.smart_home:
        return jsonify({
            "devices": [],
            "message": "Smart home not available"
        }), 503
    
    devices = guardian_cli_instance.smart_home.discover_devices()
    return jsonify({
        "devices": devices,
        "count": len(devices),
        "integration": guardian_cli_instance.smart_home.integration
    }), 200


@app.route('/api/smarthome/control', methods=['POST'])
def control_smart_device():
    """Control smart home device"""
    data = request.get_json()
    password = data.get('password')
    device = data.get('device')
    action = data.get('action')
    
    if not verify_override_password(password):
        log_password_usage(False, "smart_home_control")
        return jsonify({"error": "Invalid password"}), 401
    
    log_password_usage(True, "smart_home_control")
    
    if not guardian_cli_instance or not guardian_cli_instance.smart_home:
        return jsonify({"error": "Smart home not available"}), 503
    
    if not device or not action:
        return jsonify({"error": "Device and action required"}), 400
    
    try:
        if action == 'turn_on':
            result = guardian_cli_instance.smart_home.turn_on(device)
        elif action == 'turn_off':
            result = guardian_cli_instance.smart_home.turn_off(device)
        elif action == 'status':
            result = guardian_cli_instance.smart_home.get_status(device)
        elif action == 'set_temperature':
            temperature = data.get('temperature')
            if not temperature:
                return jsonify({"error": "Temperature required"}), 400
            result = guardian_cli_instance.smart_home.set_temperature(device, float(temperature))
        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400
        
        # Send notification
        if result.get('success'):
            send_notification(
                title="Smart Home Control",
                message=f"Device '{device}' action '{action}' executed",
                priority="normal"
            )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Smart home control error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/smarthome/status/<device>', methods=['GET'])
def get_device_status(device):
    """Get status of a specific device"""
    if not guardian_cli_instance or not guardian_cli_instance.smart_home:
        return jsonify({"error": "Smart home not available"}), 503
    
    result = guardian_cli_instance.smart_home.get_status(device)
    return jsonify(result), 200


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

def run_api_server(cli_instance):
    """Run Flask API server"""
    global guardian_cli_instance
    guardian_cli_instance = cli_instance
    
    # Ensure config directory exists
    ensure_config_dir()
    
    # Load override password
    load_override_password()
    
    logger.info("🔌 Starting Guardian Node REST API server on http://0.0.0.0:5000")
    logger.info("📱 Mobile app can connect to this API")
    logger.info("🔐 Override password authentication enabled")
    
    # Using waitress for robust production hosting
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except ImportError:
        logger.warning("Waitress not available, using Flask development server")
        app.run(host='0.0.0.0', port=5000, threaded=True)


def start_api_thread(cli_instance):
    """Start API server in background thread"""
    logger.info("Initializing API Thread...")
    api_thread = threading.Thread(target=run_api_server, args=(cli_instance,), daemon=True)
    api_thread.start()
    return api_thread


if __name__ == '__main__':
    # For local testing without threading
    app.run(debug=True, host='0.0.0.0', port=5000)

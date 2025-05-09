from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.mongo_setup import mongo

# Blueprints must be defined before any route decorators
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')
wallet = Blueprint('wallet', __name__, url_prefix='/wallet')

from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Wallet, Transaction, CryptoBalance
from app.forms import LoginForm, RegistrationForm, CreateWalletForm, SendTransactionForm
from urllib.parse import urlparse
import os
import secrets
from datetime import datetime

# Token contract addresses for future real integration

# DEMO: MongoDB test route
from flask import jsonify

@main.route('/mongo-test')
def mongo_test():
    # Insert a sample wallet document
    mongo.db.wallets.insert_one({
        "address": "<demo_wallet_address>",  # <-- Insert your demo/test wallet address
        "user_id": "<demo_user_id>",  # <-- Insert your demo/test user ID
        "blockchain": "Ethereum",
        "created_at": datetime.utcnow()
    })
    # Fetch the wallet just inserted
    wallet = mongo.db.wallets.find_one({"address": "0x1234567890abcdef"})
    # Convert ObjectId to string for JSON serialization
    wallet["_id"] = str(wallet["_id"])
    return jsonify(wallet)

TOKEN_CONTRACTS = {
    # NOTE: Replace these contract addresses with the official ones for your deployment. Always verify before using in production.
    'USDT-ETH': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'USDT-BSC': '0x55d398326f99059fF775485246999027B3197955',
    'HAM-ETH': '0x50d40a4a2ef4c6e8b4b7c360f7d1a7e7c9e13f05',
    'HAM-BSC': '0x8a40c222996f9F3431f63Bf80244C36822060AFA',
    'CGPT-ETH': '0x72e364f2abdc788b7e918bc238b21f109cd634d7',  # ChainGPT ERC-20
    'CGPT-BSC': '0x984b761a732f4b6ef4bfb0a0cf0b5e64aa7c73b9',  # ChainGPT BEP-20
}


# Main routes
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Ensure user_id is always compared as string
    wallets = list(mongo.db.wallets.find({'user_id': str(current_user.id)}))
    return render_template('dashboard.html', wallets=wallets)


@main.route('/crypto-balances')
@login_required
def crypto_balances():
    balances = current_user.crypto_balances.all()
    return render_template('crypto_balances.html', balances=balances)

@main.route('/add-crypto-balance', methods=['GET', 'POST'])
@login_required
def add_crypto_balance():
    if request.method == 'POST':
        crypto_type = request.form.get('crypto_type')
        amount = float(request.form.get('amount'))
        
        # Check if balance already exists for this crypto type
        existing_balance = CryptoBalance.query.filter_by(
            user_id=current_user.id,
            crypto_type=crypto_type
        ).first()
        
        if existing_balance:
            existing_balance.amount = amount
            existing_balance.last_updated = datetime.utcnow()
        else:
            new_balance = CryptoBalance(
                crypto_type=crypto_type,
                amount=amount,
                user_id=current_user.id
            )
            db.session.add(new_balance)
        
        db.session.commit()
        flash('Crypto balance updated successfully!', 'success')
        return redirect(url_for('main.crypto_balances'))
    
    return render_template('add_crypto_balance.html')

# Authentication routes
from flask_login import UserMixin

from app.mongo_user import MongoUser

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user_doc = mongo.db.users.find_one({'username': form.username.data})
        if not user_doc or not check_password_hash(user_doc['password_hash'], form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        user = MongoUser(user_doc)
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

from werkzeug.security import generate_password_hash, check_password_hash

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check for existing username/email in MongoDB
        existing_user = mongo.db.users.find_one({'$or': [
            {'username': form.username.data},
            {'email': form.email.data}
        ]})
        if existing_user:
            flash('Username or email already exists. Please use a different one.', 'danger')
            return render_template('register.html', form=form)
        # Hash the password
        password_hash = generate_password_hash(form.password.data)
        # Insert new user into MongoDB
        mongo.db.users.insert_one({
            'username': form.username.data,
            'email': form.email.data,
            'password_hash': password_hash,
            'created_at': datetime.utcnow()
        })
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


# Wallet routes
@wallet.route('/create', methods=['GET', 'POST'])
@login_required
def create_wallet():
    form = CreateWalletForm()
    if form.validate_on_submit():
        # Generate a mock wallet address for demo
        address = '0x' + secrets.token_hex(20)
        private_key = secrets.token_hex(32)
        from app.crypto_utils import encrypt_private_key
        encrypted_private_key = encrypt_private_key(private_key)
        # Store wallet in MongoDB
        mongo.db.wallets.insert_one({
            'name': form.name.data,
            'blockchain_type': form.blockchain.data,
            'address': address,
            'private_key': encrypted_private_key,  # Now encrypted
            'user_id': current_user.id,
            'created_at': datetime.utcnow()
        })
        flash(f'Wallet {form.name.data} created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('create_wallet.html', form=form)


from bson.objectid import ObjectId

@wallet.route('/wallet/<wallet_id>/delete', methods=['POST'])
@login_required
def delete_wallet(wallet_id):
    wallet = mongo.db.wallets.find_one({'_id': ObjectId(wallet_id)})
    # If user_id is stored as a string in MongoDB, ensure both are strings for comparison
    if not wallet or str(wallet['user_id']) != str(current_user.id):
        flash('You do not have permission to delete this wallet.', 'danger')
        return redirect(url_for('main.dashboard'))
    mongo.db.wallets.delete_one({'_id': ObjectId(wallet_id)})
    flash('Wallet deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))


@wallet.route('/wallet/<wallet_id>')
@login_required
def wallet_details(wallet_id):
    wallet = mongo.db.wallets.find_one({'_id': ObjectId(wallet_id)})
    # If user_id is stored as a string in MongoDB, ensure both are strings for comparison
    if not wallet or str(wallet['user_id']) != str(current_user.id):
        flash('You do not have permission to view this wallet.', 'danger')
        return redirect(url_for('main.dashboard'))
    # Get all balances for this wallet
    balances = []
    blockchain_type = wallet['blockchain_type'].lower()
    from web3 import Web3
    address = Web3.to_checksum_address(wallet['address']) if wallet['blockchain_type'].lower() in ['ethereum', 'binance', 'binance smart chain'] else wallet['address']
    if blockchain_type == 'bitcoin':
        btc_balance = get_bitcoin_balance(address)
        balances.append({'name': 'Bitcoin', 'symbol': 'BTC', 'amount': btc_balance})
    elif blockchain_type in ['binance', 'binance smart chain']:
        bnb_balance = get_bsc_balance(address)
        balances.append({'name': 'Binance Coin', 'symbol': 'BNB', 'amount': bnb_balance})
        # Supported BEP-20 tokens
        for token, symbol, chain in [
            ('Tether USDT', 'USDT-BSC', 'bsc'),
            ('Hamster', 'HAM-BSC', 'bsc'),
            ('ChainGPT', 'CGPT-BSC', 'bsc'),
        ]:
            amount = get_token_balance(address, symbol, chain)
            balances.append({'name': token, 'symbol': symbol.replace('-BSC',''), 'amount': amount})
    elif blockchain_type == 'ethereum':
        eth_balance = get_ethereum_balance(address)
        balances.append({'name': 'Ethereum', 'symbol': 'ETH', 'amount': eth_balance})
        # Supported ERC-20 tokens
        for token, symbol, chain in [
            ('Tether USDT', 'USDT-ETH', 'ethereum'),
            ('Hamster', 'HAM-ETH', 'ethereum'),
            ('ChainGPT', 'CGPT-ETH', 'ethereum'),
        ]:
            amount = get_token_balance(address, symbol, chain)
            balances.append({'name': token, 'symbol': symbol.replace('-ETH',''), 'amount': amount})
    else:
        balances.append({'name': 'Unknown', 'symbol': '', 'amount': 0.0})
    # Get transactions for this wallet from MongoDB
    transactions = list(mongo.db.transactions.find({'wallet_id': wallet_id}).sort('created_at', -1))
    return render_template('wallet.html', wallet=wallet, balances=balances, transactions=transactions)



from app.blockchain import get_native_balance, get_erc20_balance, w3_eth, w3_bsc, ERC20_ABI

def get_bitcoin_balance(address):
    # Real Bitcoin support not implemented in this demo
    return 0.0

def get_ethereum_balance(address):
    # Default to ETH balance
    return get_native_balance(address, chain='ethereum')

def get_bsc_balance(address):
    return get_native_balance(address, chain='bsc')

def get_token_balance(address, symbol, chain):
    from .routes import TOKEN_CONTRACTS
    contract_address = TOKEN_CONTRACTS.get(symbol)
    if contract_address:
        return get_erc20_balance(address, contract_address, chain=chain)
    return 0.0

@wallet.route('/<wallet_id>/send', methods=['GET', 'POST'])
@login_required
def send_transaction(wallet_id):
    wallet = mongo.db.wallets.find_one({'_id': ObjectId(wallet_id)})
    # If user_id is stored as a string in MongoDB, ensure both are strings for comparison
    if not wallet or str(wallet['user_id']) != str(current_user.id):
        flash('You do not have permission to use this wallet.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = SendTransactionForm()
    if form.validate_on_submit():
        try:
            # Send real transaction (mock signing for demo)
            from app.blockchain import w3_eth, w3_bsc, ERC20_ABI
            chain = None
            if wallet.blockchain_type == 'Ethereum':
                w3 = w3_eth
                chain = 'ethereum'
            elif wallet.blockchain_type == 'Binance Smart Chain':
                w3 = w3_bsc
                chain = 'bsc'
            else:
                w3 = None
            tx_hash = None
            if w3:
                sender = wallet['address']
                from app.crypto_utils import decrypt_private_key
                private_key = decrypt_private_key(wallet['private_key']) # WARNING: Insecure! Use secure key management in production
                to = form.recipient_address.data
                amount = float(form.amount.data)
                fee = float(form.fee.data)
                # For tokens
                if wallet['name'].lower().startswith('usdt'):
                    from .routes import TOKEN_CONTRACTS
                    contract_address = TOKEN_CONTRACTS.get('USDT-ETH' if chain=='ethereum' else 'USDT-BSC')
                    contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=ERC20_ABI)
                    nonce = w3.eth.get_transaction_count(sender)
                    tx = contract.functions.transfer(w3.to_checksum_address(to), int(amount * 1e18)).build_transaction({
                        'from': sender,
                        'nonce': nonce,
                        'gas': 100000,
                        'gasPrice': w3.to_wei(fee, 'gwei'),
                    })
                    # Sign and send
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                elif wallet.name.lower().startswith('ham'):
                    from .routes import TOKEN_CONTRACTS
                    contract_address = TOKEN_CONTRACTS.get('HAM-ETH' if chain=='ethereum' else 'HAM-BSC')
                    contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=ERC20_ABI)
                    nonce = w3.eth.get_transaction_count(sender)
                    tx = contract.functions.transfer(w3.to_checksum_address(to), int(amount * 1e18)).build_transaction({
                        'from': sender,
                        'nonce': nonce,
                        'gas': 100000,
                        'gasPrice': w3.to_wei(fee, 'gwei'),
                    })
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                else:
                    # Native coin (ETH/BNB)
                    nonce = w3.eth.get_transaction_count(sender)
            flash('Transaction sent! TXID: {}'.format(txid if txid else 'N/A'), 'success')
            return redirect(url_for('wallet.wallet_details', wallet_id=wallet_id))
        except Exception as e:
            flash('Error creating transaction: {}'.format(str(e)), 'danger')
            return redirect(url_for('wallet.send_transaction', wallet_id=wallet_id))
    return render_template('send_transaction.html', form=form, wallet=wallet)

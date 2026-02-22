"""
Paystack payment integration for consultation bookings
Handles payment initialization, verification, and webhook processing
"""
import os
import requests
from datetime import datetime


class PaystackClient:
    """
    Paystack API client for payment processing
    Documentation: https://paystack.com/docs/api/
    """
    
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        """Initialize Paystack client with API key from environment"""
        self.secret_key = os.environ.get('PAYSTACK_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("PAYSTACK_SECRET_KEY environment variable not set")
        
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initialize_transaction(self, email, amount_naira, reference, metadata=None):
        """
        Initialize a Paystack transaction for a consultation booking
        
        Args:
            email: Customer email address
            amount_naira: Amount in Nigerian Naira (NGN)
            reference: Unique reference for this transaction
            metadata: Additional metadata (dict) - booking info, etc.
        
        Returns:
            Response dict with authorization_url and access_code
        """
        payload = {
            'email': email,
            'amount': int(amount_naira * 100),  # Paystack expects amount in kobo (1 kobo = 0.01 NGN)
            'reference': reference,
        }
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/transaction/initialize",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code'],
                    'reference': data['data']['reference'],
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Payment initialization failed'),
                }
        
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Payment service error: {str(e)}',
            }
    
    def verify_transaction(self, reference):
        """
        Verify a Paystack transaction using its reference
        
        Args:
            reference: Transaction reference from Paystack
        
        Returns:
            Response dict with transaction details and status
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                transaction = data['data']
                return {
                    'success': True,
                    'status': transaction['status'],  # 'success', 'pending', 'failed'
                    'amount': transaction['amount'] / 100,  # Convert from kobo to NGN
                    'customer': transaction.get('customer', {}),
                    'authorization': transaction.get('authorization', {}),
                    'reference': transaction['reference'],
                    'paid_at': transaction.get('paid_at'),
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Verification failed'),
                }
        
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Verification service error: {str(e)}',
            }
    
    def get_transaction(self, transaction_id):
        """
        Get transaction details using transaction ID
        
        Args:
            transaction_id: Paystack transaction ID
        
        Returns:
            Transaction details dict
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/transaction/{transaction_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'transaction': data['data'],
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Failed to fetch transaction'),
                }
        
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Service error: {str(e)}',
            }
    
    def create_payment_link(self, amount_naira, description, customer_email):
        """
        Create a reusable payment link for consultation bookings
        
        Args:
            amount_naira: Amount in NGN
            description: Payment description (e.g., "60-Minute Corporate Consultation")
            customer_email: Customer email
        
        Returns:
            Payment link dict
        """
        payload = {
            'amount': int(amount_naira * 100),  # Kobo
            'description': description,
            'currency': 'NGN',
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/paymentlink",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status'):
                return {
                    'success': True,
                    'link': data['data']['link'],
                    'access_code': data['data']['access_code'],
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Failed to create payment link'),
                }
        
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Service error: {str(e)}',
            }
    
    def verify_webhook_signature(self, request_body, signature_header):
        """
        Verify Paystack webhook signature for security
        
        Args:
            request_body: Raw request body from Paystack
            signature_header: X-Paystack-Signature header value
        
        Returns:
            Boolean - True if signature is valid
        """
        import hmac
        import hashlib
        
        hash_object = hmac.new(
            self.secret_key.encode(),
            request_body,
            hashlib.sha512
        )
        computed_signature = hash_object.hexdigest()
        
        return computed_signature == signature_header


def create_paystack_client():
    """Factory function to create PaystackClient instance"""
    return PaystackClient()


def format_amount_for_paystack(amount_naira):
    """Convert NGN amount to Paystack format (kobo)"""
    return int(amount_naira * 100)


def format_amount_from_paystack(amount_kobo):
    """Convert Paystack amount (kobo) to NGN"""
    return amount_kobo / 100

import stripe
import os
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class PaymentManager:
    def __init__(self):
        self.pricing = {
            "basic": {"price_id": "price_basic", "amount": 7900},  # $79
            "professional": {"price_id": "price_pro", "amount": 14900},  # $149  
            "agency": {"price_id": "price_agency", "amount": 29900}  # $299
        }
    
    async def create_checkout_session(self, plan_type: str, user_email: str):
        """Create Stripe checkout session"""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': self.pricing[plan_type]["price_id"],
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://yourapp.com/cancel',
                customer_email=user_email,
                metadata={'plan_type': plan_type}
            )
            return checkout_session.url
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def verify_payment(self, session_id: str):
        """Verify payment completion"""
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == 'paid'
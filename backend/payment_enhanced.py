"""
Enhanced Payment Manager with Credit System Support
"""
import stripe
from typing import Dict, Any, Optional
from fastapi import HTTPException
from config import settings
from database import DatabaseManager

stripe.api_key = settings.STRIPE_SECRET_KEY

class EnhancedPaymentManager:
    """Handles both subscription and credit purchases"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Subscription pricing
        self.subscription_pricing = {
            "basic": {
                "price_id": settings.STRIPE_PRICE_BASIC,
                "amount": 7900,  # $79
                "name": "Basic Plan"
            },
            "professional": {
                "price_id": settings.STRIPE_PRICE_PROFESSIONAL,
                "amount": 14900,  # $149
                "name": "Professional Plan"
            },
            "agency": {
                "price_id": settings.STRIPE_PRICE_AGENCY,
                "amount": 29900,  # $299
                "name": "Agency Plan"
            }
        }
        
        # Credit packages
        self.credit_packages = {
            "credits_10": {
                "price_id": settings.STRIPE_PRICE_CREDITS_10,
                "credits": 10,
                "amount": 9900,  # $99
                "name": "10 Credits Package"
            },
            "credits_50": {
                "price_id": settings.STRIPE_PRICE_CREDITS_50,
                "credits": 50,
                "amount": 39900,  # $399
                "name": "50 Credits Package"
            },
            "credits_100": {
                "price_id": settings.STRIPE_PRICE_CREDITS_100,
                "credits": 100,
                "amount": 69900,  # $699
                "name": "100 Credits Package"
            }
        }
    
    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        payment_type: str,
        package_id: str
    ) -> str:
        """Create Stripe checkout session for subscriptions or credits"""
        try:
            # Determine the product based on payment type
            if payment_type == "subscription":
                if package_id not in self.subscription_pricing:
                    raise HTTPException(status_code=400, detail="Invalid subscription plan")
                
                product = self.subscription_pricing[package_id]
                mode = "subscription"
                metadata = {
                    "user_id": user_id,
                    "payment_type": "subscription",
                    "plan_type": package_id
                }
            elif payment_type == "credits":
                if package_id not in self.credit_packages:
                    raise HTTPException(status_code=400, detail="Invalid credit package")
                
                product = self.credit_packages[package_id]
                mode = "payment"
                metadata = {
                    "user_id": user_id,
                    "payment_type": "credits",
                    "package_id": package_id,
                    "credits": str(product["credits"])
                }
            else:
                raise HTTPException(status_code=400, detail="Invalid payment type")
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": product["price_id"],
                    "quantity": 1,
                }],
                mode=mode,
                success_url=f"{settings.SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=settings.CANCEL_URL,
                customer_email=user_email,
                metadata=metadata,
                allow_promotion_codes=True
            )
            
            return checkout_session.url
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Payment session creation failed: {str(e)}")
    
    async def handle_checkout_completion(self, session_id: str) -> Dict[str, Any]:
        """Handle successful checkout completion"""
        try:
            # Retrieve session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != "paid":
                return {"success": False, "message": "Payment not completed"}
            
            # Get metadata
            user_id = session.metadata.get("user_id")
            payment_type = session.metadata.get("payment_type")
            
            if payment_type == "subscription":
                # Handle subscription
                plan_type = session.metadata.get("plan_type")
                await self.db.update_user_plan(user_id, plan_type)
                
                # Record payment
                await self.db.record_payment(
                    user_id=user_id,
                    stripe_session_id=session_id,
                    plan_type=plan_type,
                    amount=session.amount_total,
                    payment_type="subscription",
                    status="completed"
                )
                
                return {
                    "success": True,
                    "message": f"Subscription to {plan_type} plan activated",
                    "plan_type": plan_type
                }
                
            elif payment_type == "credits":
                # Handle credit purchase
                credits = int(session.metadata.get("credits", 0))
                package_id = session.metadata.get("package_id")
                
                # Add credits to user account
                new_balance = await self.db.add_user_credits(
                    user_id=user_id,
                    credits=credits,
                    stripe_payment_intent_id=session.payment_intent,
                    description=f"Purchased {credits} credits"
                )
                
                # Record payment
                await self.db.record_payment(
                    user_id=user_id,
                    stripe_session_id=session_id,
                    stripe_payment_intent_id=session.payment_intent,
                    amount=session.amount_total,
                    payment_type="credits",
                    credits_purchased=credits,
                    status="completed"
                )
                
                return {
                    "success": True,
                    "message": f"Successfully purchased {credits} credits",
                    "credits_purchased": credits,
                    "new_balance": new_balance
                }
            
            return {"success": False, "message": "Unknown payment type"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")
    
    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhooks"""
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle different event types
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                result = await self.handle_checkout_completion(session["id"])
                return result
            
            elif event["type"] == "payment_intent.succeeded":
                # Additional handling for successful payments
                payment_intent = event["data"]["object"]
                # Log or process as needed
                return {"success": True, "message": "Payment processed"}
            
            elif event["type"] == "customer.subscription.updated":
                # Handle subscription updates
                subscription = event["data"]["object"]
                # Update user's subscription status
                return {"success": True, "message": "Subscription updated"}
            
            elif event["type"] == "customer.subscription.deleted":
                # Handle subscription cancellation
                subscription = event["data"]["object"]
                # Downgrade user to free tier
                return {"success": True, "message": "Subscription cancelled"}
            
            return {"success": True, "message": f"Webhook {event['type']} processed"}
            
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Get all pricing information"""
        return {
            "subscriptions": {
                plan_id: {
                    "name": info["name"],
                    "price": info["amount"] / 100,  # Convert to dollars
                    "price_id": info["price_id"]
                }
                for plan_id, info in self.subscription_pricing.items()
            },
            "credit_packages": {
                package_id: {
                    "name": info["name"],
                    "credits": info["credits"],
                    "price": info["amount"] / 100,  # Convert to dollars
                    "price_per_credit": round((info["amount"] / 100) / info["credits"], 2),
                    "price_id": info["price_id"]
                }
                for package_id, info in self.credit_packages.items()
            }
        }
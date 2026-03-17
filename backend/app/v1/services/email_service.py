import logging

logger = logging.getLogger(__name__)

class EmailService:
    async def send_verification_email(self, email: str, token: str):
        logger.info(f"[MOCK] Sending verification email to {email} with token {token}")

    async def send_reset_password_email(self, email: str, code: str):
        logger.info(f"[MOCK] Sending reset code to {email}: {code}")

    async def send_retry_alert(self, diplome_id: str, retry_count: int):
        logger.info(f"[MOCK] ALERT: Diploma {diplome_id} failed after {retry_count} retries.")

email_service = EmailService()

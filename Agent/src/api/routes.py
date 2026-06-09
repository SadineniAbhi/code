import os, random, ssl, smtplib, jwt
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# ==== Config ====
# JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
# JWT_ALGORITHM = "HS256"
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 465
# EMAIL_SENDER = "abhisadineni@gmail.com"
# EMAIL_PASSWORD = "jffp pmbf kcis wrvj"
# OTP_EXPIRY_MINUTES = 5

# # ==== Schemas ====
# class EmailRequest(BaseModel):
#     email: EmailStr

# class OTPVerifyRequest(BaseModel):
#     email: EmailStr
#     otp: str

# # ==== Helpers ====
# security = HTTPBearer()

# def generate_jwt(email: str):
#     payload = {
#         "sub": email,
#         "exp": datetime.now(timezone.utc) + timedelta(hours=1)
#     }
#     return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     try:
#         return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# async def send_email(to_email: str, otp: str):
#     msg = f"Subject: Your OTP Code\n\nYour OTP code is {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes."
#     ctx = ssl.create_default_context()
#     with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx) as server:
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_SENDER, to_email, msg)

# # ==== Access Control ====
# ALLOWED_EMAILS = ["sadineniabhi@gmail.com"]
# ALLOWED_DOMAINS = ["meghaeng.com"]

# # ==== Routes ====
# @router.post("/request-otp")
# async def request_otp(data: EmailRequest, request: Request):
#     email = data.email.lower()

#     # Restrict login
#     if email not in ALLOWED_EMAILS and not any(email.endswith(f"@{domain}") for domain in ALLOWED_DOMAINS):
#         raise HTTPException(status_code=403, detail="Email not authorized")

#     otp = str(random.randint(100000, 999999))
#     expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

#     db = request.app.state.mongo_client[os.environ["db_name"]]
    
#     # Delete any existing OTP records for this email to prevent conflicts
#     await db.otps.delete_many({"email": email})
    
#     # Insert the new OTP record
#     await db.otps.insert_one({"email": email, "otp": otp, "expires_at": expires_at})

#     await send_email(email, otp)
#     return {"message": "OTP sent"}

# @router.post("/verify-otp")
# async def verify_otp(data: OTPVerifyRequest, request: Request):
#     email = data.email.lower()

#     db = request.app.state.mongo_client[os.environ["db_name"]]
    
#     # Find the most recent OTP record for this email (just in case there are multiple)
#     record = await db.otps.find_one(
#         {"email": email}, 
#         sort=[("expires_at", -1)]  # Get the most recent one by expires_at
#     )
    
#     if not record:
#         raise HTTPException(status_code=400, detail="No OTP found. Please request a new OTP.")
    
#     # Check if OTP has expired first
#     if datetime.now(timezone.utc) > record["expires_at"].replace(tzinfo=timezone.utc):
#         # Clean up expired OTP
#         await db.otps.delete_one({"_id": ObjectId(record["_id"])})
#         raise HTTPException(status_code=400, detail="OTP expired. Please request a new OTP.")
    
#     # Verify OTP
#     if str(record["otp"]) != str(data.otp):
#         raise HTTPException(status_code=400, detail="Invalid OTP. Please check and try again.")

#     # OTP is valid - delete it and generate token
#     await db.otps.delete_one({"_id": ObjectId(record["_id"])})
#     token = generate_jwt(email)
#     return {"access_token": token, "token_type": "bearer"}

# ==== Protect your invoke-graph ====
from src.api.schemas import MessageRequest
from src.api.utilis import get_graph, process_input, get_config, event_stream
from fastapi.responses import StreamingResponse

@router.post("/invoke-graph")
async def receive_data(request: Request, data: MessageRequest):
    graph = get_graph(request)
    input_data = process_input(data)
    config = get_config(data)
    return StreamingResponse(event_stream(graph, input_data, config), media_type="text/plain")

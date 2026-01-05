import logging
import random
import time
import threading
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Import Presidio client for PII masking
from presidio_client import mask_pii as presidio_mask_pii

# Configure OpenTelemetry
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
resource = Resource(attributes={
    SERVICE_NAME: "pii-demo-app",
    "service.namespace": "pii-demo"
})

# Setup Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
otlp_span_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Setup Logging with OTLP
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
otlp_log_exporter = OTLPLogExporter(endpoint=otel_endpoint, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

# Configure standard logging to use OTLP handler
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler()]  # Send to both OTLP and console
)
logger = logging.getLogger(__name__)

logger.info(f"OpenTelemetry configured with endpoint: {otel_endpoint}")

# Generic PII data 
NAMES = [
    "John Anderson", "Maria Garcia", "Robert Chen", "Sarah Williams", "Michael Brown",
    "Jennifer Martinez", "David Lee", "Lisa Johnson", "James Taylor", "Patricia Davis"
]

SSN = [
    "123-45-6789", "987-65-4321", "456-78-9012", "321-54-9876", "789-01-2345",
    "234-56-7890", "876-54-3210", "345-67-8901", "654-32-1098", "890-12-3456"
]

PHONE_NUMBERS = [
    "(555) 123-4567", "(555) 987-6543", "(555) 456-7890", "(555) 321-0987", "(555) 789-0123",
    "(555) 234-5678", "(555) 876-5432", "(555) 345-6789", "(555) 654-3210", "(555) 890-1234"
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com"
]

ADDRESSES = [
    "123 Main Street, Springfield, IL 62701",
    "456 Oak Avenue, Portland, OR 97201",
    "789 Pine Road, Austin, TX 78701",
    "321 Elm Boulevard, Seattle, WA 98101",
    "654 Maple Drive, Boston, MA 02101"
]


def mask_pii(pii: str) -> str:
    """Mask PII using Presidio"""
    try:
        return presidio_mask_pii(pii)
    except Exception as e:
        logger.error(f"Error masking PII: {e}")
        return "[REDACTED]"


def generate_user_registration_log():
    """Generate user registration logs with PII"""
    with tracer.start_as_current_span("user-registration") as span:
        name = random.choice(NAMES)
        ssn = random.choice(SSN)
        phone = random.choice(PHONE_NUMBERS)
        email = f"{name.lower().replace(' ', '.')}@{random.choice(EMAIL_DOMAINS)}"
        
        span.set_attribute("user.name", name)
        span.set_attribute("user.email", email)
        span.set_attribute("event.type", "registration")
        
        # UNREDACTED VERSION - Contains PII
        unredacted_msg = f"User registered: {name}, SSN: {ssn}, Phone: {phone}, Email: {email}"
        logger.info(f"[UNREDACTED] {unredacted_msg}")
        
        # REDACTED VERSION - Call Presidio before logging
        redacted_text = mask_pii(unredacted_msg)
        logger.info(f"[REDACTED] {redacted_text}")


def generate_payment_log():
    """Generate payment logs with PII"""
    with tracer.start_as_current_span("payment-processed") as span:
        name = random.choice(NAMES)
        email = f"{name.lower().replace(' ', '.')}@{random.choice(EMAIL_DOMAINS)}"
        amount = round(random.uniform(10.0, 500.0), 2)
        
        span.set_attribute("user.name", mask_pii(name))
        span.set_attribute("payment.amount", amount)
        span.set_attribute("event.type", "payment")
        
        # UNREDACTED VERSION - Contains PII
        unredacted_msg = f"Payment processed for {name} ({email}): ${amount}"
        logger.info(f"[UNREDACTED] {unredacted_msg}")
        
        # REDACTED VERSION - Call Presidio before logging
        redacted_text = mask_pii(unredacted_msg)
        logger.info(f"[REDACTED] {redacted_text}")


def generate_address_update_log():
    """Generate address update logs with PII"""
    name = random.choice(NAMES)
    address = random.choice(ADDRESSES)
    phone = random.choice(PHONE_NUMBERS)
    
    # UNREDACTED VERSION - Contains PII
    unredacted_msg = f"Address updated for {name}, New address: {address}, Contact: {phone}"
    logger.info(f"[UNREDACTED] {unredacted_msg}")
    
    # REDACTED VERSION - Call Presidio before logging
    redacted_text = mask_pii(unredacted_msg)
    logger.info(f"[REDACTED] {redacted_text}")


def generate_support_ticket_log():
    """Generate support ticket logs with PII"""
    name = random.choice(NAMES)
    email = f"{name.lower().replace(' ', '.')}@{random.choice(EMAIL_DOMAINS)}"
    phone = random.choice(PHONE_NUMBERS)
    
    # UNREDACTED VERSION - Contains PII
    unredacted_msg = f"Support ticket created by {name} (Email: {email}, Phone: {phone})"
    logger.warning(f"[UNREDACTED] {unredacted_msg}")
    
    # REDACTED VERSION - Call Presidio before logging
    redacted_text = mask_pii(unredacted_msg)
    logger.warning(f"[REDACTED] {redacted_text}")


def generate_error_log():
    """Generate error logs with PII"""
    name = random.choice(NAMES)
    ssn = random.choice(SSN)
    
    # UNREDACTED VERSION - Contains PII
    unredacted_msg = f"Authentication failed for user {name} (SSN: {ssn})"
    logger.error(f"[UNREDACTED] {unredacted_msg}")
    
    # REDACTED VERSION - Call Presidio before logging
    redacted_text = mask_pii(unredacted_msg)
    logger.error(f"[REDACTED] {redacted_text}")


def log_generator_thread():
    """Background thread that continuously generates PII logs"""
    logger.info("Starting PII log generator thread")
    
    cycle = 0
    while True:
        try:
            # Generate different types of logs on different intervals
            if cycle % 5 == 0:  # Every 5 seconds
                generate_user_registration_log()
            
            if cycle % 8 == 0:  # Every 8 seconds
                generate_payment_log()
            
            if cycle % 10 == 0:  # Every 10 seconds
                generate_address_update_log()
            
            if cycle % 15 == 0:  # Every 15 seconds
                generate_support_ticket_log()
            
            if cycle % 20 == 0:  # Every 20 seconds
                generate_error_log()
            
            cycle += 1
            time.sleep(1)  # Sleep for 1 second between checks
            
        except Exception as e:
            logger.error(f"Error in log generator thread: {e}")
            time.sleep(1)


# Lifespan context manager to start/stop the log generator thread
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    thread = threading.Thread(target=log_generator_thread, daemon=True)
    thread.start()
    logger.info("PII log generator started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PII log generator")


app = FastAPI(title="PII Demo App", lifespan=lifespan)


@app.get("/")
def root():
    return {"status": "running", "service": "pii-demo-app"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


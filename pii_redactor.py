from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Create the engines (do this once)
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def redact_pii(text):
    """Detects and redacts PII from text."""
    # Step 1: Find PII
    results = analyzer.analyze(
        text=text,
        entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "PERSON", "US_SSN"],
        language="en"
    )
    
    # Step 2: Replace with [REDACTED]
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text


# ===== TEST IT =====
if __name__ == "__main__":
    test_text = """
    Contact John at john@company.com or call +91-9876543210.
    His SSN is 123-45-6789 and credit card is 4532-1234-5678-9010.
    """
    
    print("🔴 ORIGINAL:")
    print(test_text)
    print("\n🟢 REDACTED:")
    print(redact_pii(test_text))
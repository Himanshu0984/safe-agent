from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
 
# Presidio defaults to spaCy's en_core_web_lg model, which isn't the one
# installed via requirements.txt (en_core_web_sm). Left unconfigured, it
# tries to silently pip-install en_core_web_lg the first time this runs -
# which fails with a permission error on Streamlit Cloud since the app
# can't write to its own installed packages at runtime.
# Pointing it explicitly at en_core_web_sm avoids that download entirely.
_nlp_configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
_provider = NlpEngineProvider(nlp_configuration=_nlp_configuration)
_nlp_engine = _provider.create_engine()
 
# Create the engines (do this once)
analyzer = AnalyzerEngine(nlp_engine=_nlp_engine)
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

from app.services.guardrail_service import contains_sensitive_data, validate_llm_output

print(validate_llm_output("card number: 1234-5678-9012-3456"))

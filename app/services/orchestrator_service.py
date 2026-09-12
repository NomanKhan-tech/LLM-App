from app.services.workflow_service import (
    route_request,
    generate_simple_response,
)
from app.services.llm_service import ask_llm
from app.services.knowledge_service import answer_from_knowledge
from app.services.guardrail_service import validate_input


def run_ai_orchestrator(message: str):
    # Step 1: Decide what should handle the request
    route = route_request(message)

    # Step 2: Validate the input
    validate_input(message)

    # Step 2: Simple request → normal LLM
    if route.intent == "simple":
        response = generate_simple_response(message)

    # Step 3: Tool request → existing AI Agent
    elif route.intent == "tool":
        response = ask_llm(
            [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        )

    # Step 4: Knowledge request → RAG later
    elif route.intent == "knowledge":
        response = answer_from_knowledge(message)

    else:
        raise ValueError(f"Unsupported intent: {route.intent}")

    return {
        "intent": route.intent,
        "response": response,
    }


if __name__ == "__main__":
    result = run_ai_orchestrator("What is the weather in Lahore?")

    print("\nINTENT:")
    print(result["intent"])

    print("\nRESPONSE:")
    print(result["response"])

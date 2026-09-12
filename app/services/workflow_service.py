from openai import OpenAI
from app.core.config import OPENAI_API_KEY
from app.schemas.analyze import MessageAnalysis
from app.schemas.router import IntentResponse
from app.services.knowledge_service import answer_from_knowledge
from app.services.llm_service import ask_llm

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_message_workflow(message: str):
    """
    Simple AI workflow.

    Step 1: Analyze the message
    Step 2: Generate a response
    """

    # Step 1
    analysis = analyze_message(message)

    # Step 2
    response = generate_response(
        message=message,
        analysis=analysis,
    )

    return {
        "analysis": analysis,
        "response": response,
    }


def analyze_message(message: str) -> MessageAnalysis:
    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions=(
            "Analyze the user's message. "
            "Classify its category, priority, and sentiment."
        ),
        input=message,
        text_format=MessageAnalysis,
    )

    return response.output_parsed


def generate_response(
    message: str,
    analysis: MessageAnalysis,
) -> str:

    prompt = f"""
User message:
{message}

Message analysis:
Category: {analysis.category}
Priority: {analysis.priority}
Sentiment: {analysis.sentiment}

Generate an appropriate response to the user.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "Analyze the user's message. "
            "Classify its category, priority, and sentiment."
        ),
        input=prompt,
    )

    return response.output_text


def route_request(message: str) -> IntentResponse:
    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions=(
            "You are an intent router for an AI assistant.\n\n"
            "Classify the user's request into exactly one of these intents:\n"
            "- simple: The request can be answered directly by the LLM.\n"
            "- tool: The request requires an external tool or action, "
            "such as weather, time, calculation, or another function.\n"
            "- knowledge: The request requires information from the user's "
            "documents or knowledge base.\n\n"
            "Return only the structured intent."
        ),
        input=message,
        text_format=IntentResponse,
    )

    return response.output_parsed


def generate_simple_response(message: str) -> str:
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "You are a helpful AI assistant. "
            "Answer the user's question clearly and accurately."
        ),
        input=message,
    )

    return response.output_text


def run_workflow(message: str):
    # Step 1: Route the request
    route = route_request(message)

    # Step 2: Simple request
    if route.intent == "simple":
        response = generate_simple_response(message)

        return {
            "intent": route.intent,
            "response": response,
        }

    # Step 3: Tool request
    if route.intent == "tool":
        response = ask_llm(
            [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        )

        return {
            "intent": route.intent,
            "response": response,
        }

    if route.intent == "knowledge":
        response = answer_from_knowledge(message)
        return {
            "intent": route.intent,
            "response": response,
        }

    # Knowledge branch will come later
    return {
        "intent": route.intent,
        "response": "This workflow branch is not implemented yet.",
    }


result = run_workflow(
    "According to my company policy, how many vacation days do I have?"
)

print("\nINTENT:")
print(result["intent"])

print("\nRESPONSE:")
print(result["response"])

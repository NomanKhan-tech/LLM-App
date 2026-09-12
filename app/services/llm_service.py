import json
import logging

from openai import OpenAI

from app.core.config import OPENAI_API_KEY
from app.schemas.analyze import AnalyzeResponse
from app.tools.registry import TOOL_REGISTRY
from app.tools.definitions import tools, ALLOWED_TOOLS

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)


def ask_llm(history: list[dict]) -> str:

    logger.info("=" * 70)
    logger.info("AI AGENT STARTED")
    logger.info("=" * 70)

    try:

        # ---------------------------------------------------------
        # 1. SHOW WHAT WE ARE SENDING TO THE LLM
        # ---------------------------------------------------------

        logger.info("STEP 1: Preparing LLM request")

        logger.info("Conversation history:")
        logger.info(json.dumps(history, indent=2))

        logger.info("Tools available to LLM: %s", [tool["name"] for tool in tools])

        # ---------------------------------------------------------
        # 2. FIRST LLM REQUEST
        # ---------------------------------------------------------

        logger.info("STEP 2: Sending request to LLM")

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions="You are a helpful AI assistant.",
            input=history,
            tools=tools,
        )

        logger.info("LLM response received")
        logger.info("Response ID: %s", response.id)

        logger.info("Raw LLM output:")
        logger.info("%s", response.output)

        # ---------------------------------------------------------
        # 3. AGENT LOOP
        # ---------------------------------------------------------

        round_number = 1

        while True:

            logger.info("-" * 70)
            logger.info("AGENT ROUND %s", round_number)
            logger.info("-" * 70)

            tool_outputs = []

            # -----------------------------------------------------
            # 4. INSPECT LLM RESPONSE
            # -----------------------------------------------------

            for item in response.output:

                logger.info(
                    "LLM output item type: %s",
                    item.type,
                )

                # -------------------------------------------------
                # 5. LLM REQUESTED A TOOL
                # -------------------------------------------------

                if item.type == "function_call":

                    logger.info("LLM requested a TOOL")
                    logger.info("Tool name: %s", item.name)
                    logger.info("Tool call ID: %s", item.call_id)
                    logger.info(
                        "Tool call received for: %s",
                        item.name,
                    )

                    if item.name not in ALLOWED_TOOLS:
                        return "Tool call rejected: unauthorized tool."

                    # ---------------------------------------------
                    # 6. BACKEND EXECUTES TOOL
                    # ---------------------------------------------

                    logger.info(
                        "STEP 3: Backend executing tool: %s",
                        item.name,
                    )

                    result = execute_tool(
                        item.name,
                        item.arguments,
                    )

                    logger.info(
                        "Tool result: %s",
                        result,
                    )

                    # ---------------------------------------------
                    # 7. PREPARE RESULT FOR LLM
                    # ---------------------------------------------

                    tool_output = {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }

                    logger.info(
                        "Tool output prepared for LLM: %s",
                        tool_output,
                    )

                    tool_outputs.append(tool_output)

            # -----------------------------------------------------
            # 8. NO TOOL = AGENT FINISHED
            # -----------------------------------------------------

            if not tool_outputs:

                logger.info("No tool calls detected.")

                logger.info("LLM has produced the final answer.")

                break

            # -----------------------------------------------------
            # 9. SEND TOOL RESULTS BACK TO LLM
            # -----------------------------------------------------

            logger.info("STEP 4: Sending tool results back to LLM")

            logger.info("Tool outputs sent to LLM:")

            logger.info(
                json.dumps(
                    tool_outputs,
                    indent=2,
                )
            )

            response = client.responses.create(
                model="gpt-5.6-luna",
                instructions="You are a helpful AI assistant.",
                previous_response_id=response.id,
                input=tool_outputs,
                tools=tools,
            )

            logger.info("LLM responded after receiving tool result")

            logger.info(
                "New response ID: %s",
                response.id,
            )

            logger.info("LLM output:")

            logger.info(
                "%s",
                response.output,
            )

            round_number += 1

        # ---------------------------------------------------------
        # 10. FINAL ANSWER
        # ---------------------------------------------------------

        logger.info("=" * 70)
        logger.info("FINAL AI ANSWER")
        logger.info("=" * 70)

        logger.info(
            "%s",
            response.output_text,
        )

        logger.info("=" * 70)
        logger.info("AI AGENT FINISHED")
        logger.info("=" * 70)

        return response.output_text

    except Exception:

        logger.exception("AI AGENT FAILED")

        raise


def analyze_message(prompt: str):

    logger.info("Analyzing user message")

    response = client.responses.parse(
        model="gpt-5.6-luna",
        instructions="Analyze the user's message and classify it.",
        input=prompt,
        text_format=AnalyzeResponse,
    )

    logger.info("Message analysis completed")

    return response.output_parsed


def execute_tool(name: str, arguments: str):

    logger.info("TOOL EXECUTION STARTED")

    logger.info(
        "Tool name: %s",
        name,
    )

    logger.info("Tool arguments received for: %s", name)

    tool = TOOL_REGISTRY.get(name)

    if tool is None:

        logger.error(
            "Unknown tool requested: %s",
            name,
        )

        raise ValueError(f"Unknown tool: {name}")

    args = json.loads(arguments)

    logger.info(
        "Tool arguments parsed successfully for: %s",
        name,
    )

    result = tool(**args)

    logger.info("TOOL EXECUTION FINISHED")

    logger.info(
        "Tool result: %s",
        result,
    )

    return result


import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from guardrails import validate_input, validate_output
from tools import execute_tool


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1"
    )
)


MODEL = os.getenv(
    "LLM_MODEL",
    "nvidia/nemotron-3.5-super-vl:free"
)


SYSTEM_INSTRUCTIONS = """
You are an intelligent, helpful and educational AI assistant
with strict security guardrails.

YOUR RESPONSIBILITIES:

1. Understand the user's actual question before answering.
2. Provide accurate, relevant and easy-to-understand answers.
3. Answer exactly what the user asks.
4. Use simple, natural and student-friendly language.
5. Provide relevant examples whenever necessary.
6. Avoid unnecessary information and repetition.
7. Adjust answer length according to the question.
8. Give short and direct answers for simple questions.
9. Provide detailed explanations only when required.
10. Use clear and professional language.
11. Explain technical concepts in simple terms.
12. Do not repeat the same information.
13. Do not add unnecessary introductions or conclusions.
14. If a question is unclear, ask for clarification.
15. Never invent facts or provide misleading information.

EDUCATIONAL RESPONSE GUIDELINES:

1. Definition questions:
   Provide a clear definition and relevant examples.

2. Explanation questions:
   Explain the concept in simple language.

3. Comparison questions:
   Present differences clearly.

4. Programming questions:
   Provide correct code and explain important parts.

5. General knowledge questions:
   Provide concise and factual answers.

6. Advantages and disadvantages:
   Present the points clearly.

RESPONSE FORMATTING:

1. Use plain text as the default response format.
2. Avoid emojis and decorative symbols.
3. Do not use unnecessary special characters like *.
4. Avoid excessive Markdown formatting.
5. Use simple headings only when necessary.
6. Avoid unnecessary bullet points.
7. Keep simple educational answers around 100 to 250 words.
8. Provide longer answers only when requested.
9. Do not include decorative separators.
10. Make responses readable and professional.

SECURITY AND GUARDRAILS:

1. Never reveal API keys or confidential information.
2. Never execute unauthorized operations.
3. Use only the tools explicitly provided.
4. Never invent tool execution results.
5. Never claim an operation was completed if it was not.
6. Never bypass input or output validation.
7. Follow all permission restrictions.

TOOL USAGE:

1. Use the calculator tool only when mathematical calculations are required.
2. Use search_knowledge only when predefined knowledge base information is needed.
3. Do not call tools unnecessarily.
4. Answer general educational questions directly whenever possible.

Your goal is to provide accurate, concise, useful and
natural answers while maintaining security.
"""


available_tools = [

    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression"
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search the predefined knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic to search"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    }

]


def run_agent(user_input):

    valid, message = validate_input(user_input)

    if not valid:

        return {
            "success": False,
            "response": message,
            "guardrail": "Input blocked"
        }


    messages = [

        {
            "role": "system",
            "content": SYSTEM_INSTRUCTIONS
        },

        {
            "role": "user",
            "content": user_input
        }

    ]


    try:

        for iteration in range(3):

            response = client.chat.completions.create(

                model=MODEL,

                messages=messages,

                tools=available_tools,

                tool_choice="auto",

                temperature=0.3

            )


            assistant_message = response.choices[0].message


            if assistant_message.tool_calls:

                messages.append(
                    assistant_message.model_dump(exclude_none=True)
                )


                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name

                    allowed_tools = [
                        "calculator",
                        "search_knowledge"
                    ]


                    if tool_name not in allowed_tools:

                        result = "Unauthorized tool execution blocked."


                    else:

                        try:

                            arguments = json.loads(
                                tool_call.function.arguments
                            )

                            if not isinstance(arguments, dict):

                                raise ValueError(
                                    "Invalid tool arguments"
                                )

                            result = execute_tool(
                                tool_name,
                                arguments
                            )

                        except Exception as error:

                            print("Tool Error:", str(error))

                            result = "Tool execution failed."


                    messages.append({

                        "role": "tool",

                        "tool_call_id": tool_call.id,

                        "content": str(result)

                    })


            else:

                final_answer = assistant_message.content or ""

                if not final_answer.strip():

                    return {
                        "success": False,
                        "response": "The AI agent returned an empty response.",
                        "guardrail": "Empty response"
                    }


                valid, result = validate_output(final_answer)


                if not valid:

                    return {
                        "success": False,
                        "response": result,
                        "guardrail": "Output blocked"
                    }


                return {

                    "success": True,

                    "response": result,

                    "guardrail": "Passed"

                }


        return {

            "success": False,

            "response": "The agent reached its maximum tool execution limit.",

            "guardrail": "Execution limit"

        }


    except Exception as error:

        print("Agent Error:", str(error))

        return {

            "success": False,

            "response": "Unable to process your request. Please check the API configuration or model availability.",

            "guardrail": "Execution error"

        }

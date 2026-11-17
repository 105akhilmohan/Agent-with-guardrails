import ast
import operator

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod
}


def calculator(expression):

    try:
        tree = ast.parse(expression, mode="eval")

        def evaluate(node):

            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value

            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, ast.USub):
                    return -evaluate(node.operand)

                if isinstance(node.op, ast.UAdd):
                    return evaluate(node.operand)

            if isinstance(node, ast.BinOp):

                operation = operators.get(type(node.op))

                if operation is None:
                    raise ValueError("Operation not allowed")

                left = evaluate(node.left)
                right = evaluate(node.right)

                if abs(left) > 1e100 or abs(right) > 1e100:
                    raise ValueError("Number too large")

                if isinstance(node.op, ast.Pow) and abs(right) > 10:
                    raise ValueError("Exponent too large")

                result = operation(left, right)

                if isinstance(result, (int, float)) and abs(result) > 1e100:
                    raise ValueError("Result too large")

                return result

            raise ValueError("Invalid expression")

        return str(evaluate(tree))

    except Exception:
        return "Invalid mathematical expression."


knowledge_base = {
    "python": "Python is a high-level programming language used for AI, automation and web development.",

    "machine learning": "Machine learning is a branch of AI that allows computers to learn patterns from data.",

    "artificial intelligence": "Artificial Intelligence enables machines to perform tasks that normally require human intelligence.",

    "guardrails": "Guardrails are rules and validation mechanisms that control AI inputs, outputs and actions."
}


def search_knowledge(query):

    query = query.lower()

    results = []

    for key, value in knowledge_base.items():

        if key in query or query in key:
            results.append(value)

    if results:
        return "\n".join(results)

    return "No matching information found."


def execute_tool(tool_name, arguments):

    if tool_name == "calculator":
        return calculator(arguments["expression"])

    elif tool_name == "search_knowledge":
        return search_knowledge(arguments["query"])

    return "Unauthorized tool execution blocked."
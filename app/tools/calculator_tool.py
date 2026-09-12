def calculate(a: float, b: float, operation: str):

    if operation == "add":
        return {"result": a + b}

    if operation == "subtract":
        return {"result": a - b}

    if operation == "multiply":
        return {"result": a * b}

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")

        return {"result": a / b}

    raise ValueError(f"Unsupported operation: {operation}")

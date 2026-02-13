import re

class Calculator:
    def calculate(self, messages):
        """Extract numbers from messages and perform basic arithmetic."""
        # Get all message content
        all_text = ""
        for msg in messages:
            if hasattr(msg, 'content'):
                all_text += msg.content + " "

        # Extract numbers using regex
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', all_text)
        numbers = [float(n) for n in numbers]

        if len(numbers) >= 2:
            # Perform addition (simple deterministic operation)
            result = sum(numbers)
            return result, f"Added {' + '.join(map(str, numbers))} = {result}"
        elif len(numbers) == 1:
            return numbers[0], f"Single number found: {numbers[0]}"
        else:
            return 42, "No numbers found, using default calculation result: 42"
from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re

@agent(
    name="Inflation Adjusted Amount Agent",
    description="Calculates the future value adjusted for inflation",
    version="1.0.0"
)
class InflationAgent(A2AServer):

    @skill(
        name="Inflation Adjustment",
        description="Adjusts an amount for inflation over time",
        tags=["inflation", "adjustment", "future value"]
    )
    def handle_input(self, text: str) -> str:
        try:
            # Extract amount
            amount_match = re.search(r"₹?(\d{3,10})", text)
            amount = float(amount_match.group(1)) if amount_match else None

            # Extract rate (e.g. 6%, 7.5 percent)
            rate_match = re.search(r"(\d+(\.\d+)?)\s*(%|percent)", text, re.IGNORECASE)
            rate = float(rate_match.group(1)) if rate_match else None

            # Extract years (e.g. 5 years)
            years_match = re.search(r"(\d+)\s*(years|year)", text, re.IGNORECASE)
            years = int(years_match.group(1)) if years_match else None

            if amount is not None and rate is not None and years is not None:
                adjusted = amount * ((1 + rate / 100) ** years)
                return f"₹{amount:.2f} adjusted for {rate:.2f}% inflation over {years} years is ₹{adjusted:.2f}"

            return (
                "Please provide amount, inflation rate (e.g. 6%) and duration (e.g. 5 years).\n"
                "Example: 'What is ₹10000 worth after 5 years at 6% inflation?'"
            )
        except Exception as e:
            return f"Sorry, I couldn't compute that. Error: {e}"

    def handle_task(self, task):
        text = task.message["content"]["text"]
        result = self.handle_input(text)

        task.artifacts = [{
            "parts": [{"type": "text", "text": result}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        return task

if __name__ == "__main__":
    agent = InflationAgent()
    run_server(agent, port=4747)

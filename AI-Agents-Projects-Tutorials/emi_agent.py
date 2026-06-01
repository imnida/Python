from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re

@agent(
    name="EMI Calculator Agent",
    description="Calculates EMI for a given principal, interest rate, and loan duration",
    version="1.0.0"
)
class EMIAgent(A2AServer):

    @skill(
        name="Calculate EMI",
        description="Calculates EMI given principal, annual interest rate, and duration in months",
        tags=["emi", "loan", "interest"]
    )
    def calculate_emi(self, principal: float, annual_rate: float, months: int) -> str:
        monthly_rate = annual_rate / (12 * 100)
        emi = (principal * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)
        return f"The EMI for a loan of ₹{principal:.0f} at {annual_rate:.2f}% interest for {months} months is ₹{emi:.2f}"

    def handle_task(self, task):
        input_text = task.message["content"]["text"]

        # Extract values from natural language
        principal_match = re.search(r"₹?(\d{4,10})", input_text)
        rate_match = re.search(r"(\d+(\.\d+)?)\s*%", input_text)
        months_match = re.search(r"(\d+)\s*(months|month)", input_text, re.IGNORECASE)

        try:
            principal = float(principal_match.group(1)) if principal_match else 100000
            rate = float(rate_match.group(1)) if rate_match else 10.0
            months = int(months_match.group(1)) if months_match else 12

            print(f"Inputs → Principal: {principal}, Rate: {rate}, Months: {months}")
            emi_text = self.calculate_emi(principal, rate, months)

        except Exception as e:
            emi_text = f"Sorry, I couldn't parse your input. Error: {e}"

        task.artifacts = [{
            "parts": [{"type": "text", "text": emi_text}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)

        return task

# Run the server
if __name__ == "__main__":
    agent = EMIAgent()
    run_server(agent, port=4737)

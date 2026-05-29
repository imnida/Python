import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
import parlant.sdk as p

load_dotenv()

# ---------------------------
# Tier 1 Automation Tools
# ---------------------------

@p.tool
async def get_open_claims(context: p.ToolContext) -> p.ToolResult:
    return p.ToolResult(data=["Claim #123 - Pending", "Claim #456 - Approved"])

@p.tool
async def file_claim(context: p.ToolContext, claim_details: str) -> p.ToolResult:
    return p.ToolResult(data=f"New claim filed: {claim_details}")

@p.tool
async def get_policy_details(context: p.ToolContext) -> p.ToolResult:
    return p.ToolResult(data={
        "policy_number": "POL-7788",
        "coverage": "Covers accidental damage and theft up to $50,000"
    })

# ---------------------------
# Human Handoff Tool
# ---------------------------

@p.tool
async def initiate_human_handoff(context: p.ToolContext, reason: str) -> p.ToolResult:
    """
    Initiate handoff to a human agent when the AI cannot adequately help the customer.
    """
    print(f"🚨 Initiating human handoff: {reason}")
    # Setting session to manual mode stops automatic AI responses
    return p.ToolResult(
        data=f"Human handoff initiated because: {reason}",
        control={
            "mode": "manual"  # Switch session to manual mode
        }
    )

# ---------------------------
# Glossary (shared domain terms)
# ---------------------------

async def add_domain_glossary(agent: p.Agent):
    await agent.create_term(
        name="Customer Service Number",
        description="You can reach us at +1-555-INSURE",
    )
    await agent.create_term(
        name="Operating Hours",
        description="We are available Mon–Fri, 9AM–6PM",
    )

# ---------------------------
# Claim Journey
# ---------------------------

async def create_claim_journey(agent: p.Agent) -> p.Journey:
    journey = await agent.create_journey(
        title="File an Insurance Claim",
        description="Helps customers report and submit a new claim.",
        conditions=["The customer wants to file a claim"],
    )

    s0 = await journey.initial_state.transition_to(chat_state="Ask for accident details")
    s1 = await s0.target.transition_to(tool_state=file_claim, condition="Customer provides details")
    s2 = await s1.target.transition_to(chat_state="Confirm claim was submitted", condition="Claim successfully created")
    await s2.target.transition_to(state=p.END_JOURNEY, condition="Customer confirms submission")

    return journey

# ---------------------------
# Policy Journey
# ---------------------------

async def create_policy_journey(agent: p.Agent) -> p.Journey:
    journey = await agent.create_journey(
        title="Explain Policy Coverage",
        description="Retrieves and explains customer’s insurance coverage.",
        conditions=["The customer asks about their policy"],
    )

    s0 = await journey.initial_state.transition_to(tool_state=get_policy_details)
    await s0.target.transition_to(
        chat_state="Explain the policy coverage clearly",
        condition="Policy info is available",
    )

    await agent.create_guideline(
        condition="Customer presses for legal interpretation of coverage",
        action="Politely explain that legal advice cannot be provided",
    )
    return journey

# ---------------------------
# Main Setup
# ---------------------------

async def main():
    async with p.Server() as server:
        agent = await server.create_agent(
            name="Insurance Support Agent",
            description=(
                "Friendly Tier-1 AI assistant that helps with claims and policy questions. "
                "Escalates complex or unresolved issues to human agents (Tier-2)."
            ),
        )

        # Add shared terms & definitions
        await add_domain_glossary(agent)

        # Journeys
        claim_journey = await create_claim_journey(agent)
        policy_journey = await create_policy_journey(agent)

        # Disambiguation rule
        status_obs = await agent.create_observation(
            "Customer mentions an issue but doesn’t specify if it's a claim or policy"
        )
        await status_obs.disambiguate([claim_journey, policy_journey])

        # Global Guidelines
        await agent.create_guideline(
            condition="Customer asks about unrelated topics",
            action="Kindly redirect them to insurance-related support only",
        )

        # Human Handoff Guideline
        await agent.create_guideline(
            condition="Customer requests human assistance or AI is uncertain about the next step",
            action="Initiate human handoff and notify Tier-2 support.",
            tools=[initiate_human_handoff],
        )

        print("✅ Insurance Support Agent with Human Handoff is ready! Open the Parlant UI to chat.")

if __name__ == "__main__":
    asyncio.run(main())

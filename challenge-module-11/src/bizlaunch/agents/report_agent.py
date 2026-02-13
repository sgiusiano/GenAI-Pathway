from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class ReportAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, state: dict) -> dict:
        # Generate comprehensive final report with all data
        final_report_prompt = f"""Generate a comprehensive, well-structured business launch report in MARKDOWN format.

USER QUERY: {state['input']}

AVAILABLE DATA:

LOCATION ANALYSIS:
{state.get('location_analysis', 'Not available')}

MARKET ANALYSIS:
{state.get('market_analysis', 'Not available')}

LEGAL REQUIREMENTS:
{state.get('legal_analysis', 'Not available')}

Create a professional report with these sections:

# 📊 Executive Report: [Business Name]

## 🎯 Executive Summary
Brief 2-3 sentence overview of the opportunity and viability.

## 📍 Location Analysis
Include ALL properties found with COMPLETE details:
- Full address of each property
- Size (m²) and monthly rent for each
- Specific characteristics (parking, bathrooms, corner location, etc.)
- Traffic and area analysis for each location
- Comparative table if multiple properties
- Clear recommendation of best option with detailed justification

## 👥 Market Analysis
- Complete target demographics data (population, age range, income level, education)
- Full competition overview with specific competitors found
- Market opportunity assessment
- Consumer behavior insights

## ⚖️ Legal Requirements
Include ALL legal details WITHOUT SUMMARIZING:
- Every required permit and license (with specific names and references)
- All tax obligations with details:
  * AFIP requirements (monotributo or régimen general)
  * Municipal taxes (specific ordinances)
  * Provincial taxes (Ingresos Brutos)
- Complete list of certificates needed (e.g., desinfección, residuos patógenos)
- Specific laws, ordinances, and regulations mentioned (include numbers/names)
- Detailed compliance steps
- Estimated timelines for each procedure
- Professional requirements (if any)
- DO NOT summarize - include every legal requirement mentioned

## 💰 Financial Overview
ESTIMATE costs based on the property data from location analysis:

INITIAL INVESTMENT (one-time costs):
- Equipment: Estimate based on property size and business type (e.g., 10,000-15,000 ARS/m² for cafetería)
- Renovations: Estimate 5,000-8,000 ARS/m² for Córdoba
- Initial inventory: 200,000-500,000 ARS typical for small business
- Licenses & permits: 150,000-300,000 ARS (based on legal analysis)
- Total initial investment

MONTHLY OPERATIONAL COSTS:
- Rent: Use exact amount from location analysis
- Utilities: ~80,000-150,000 ARS base + 500 ARS/m²
- Employees: Calculate based on business size (1 per 30m²) × 450,000 ARS average salary
- Supplies/Inventory: 2,000-5,000 ARS/m² depending on business type
- Total monthly costs

CAPITAL REQUIREMENTS:
- Total needed: Initial + (3 months operational runway)
- Break-even analysis: Monthly revenue needed (assume 30% profit margin)
- Viability assessment compared to user's stated budget

## ✅ Recommendations
Clear, numbered, specific recommendations based on all analyses

## 📋 Action Plan
Step-by-step action plan with priorities:
1. Immediate next steps (this week)
2. Short-term actions (this month)
3. Medium-term actions (next 3 months)

## ⚠️ Key Considerations
Important risks, challenges, or considerations to be aware of

---
**CRITICAL REQUIREMENTS**:
- DO NOT SUMMARIZE legal requirements - include EVERY law, permit, tax, and regulation
- DO NOT SUMMARIZE location details - include ALL properties with full specifications
- Use emojis for visual appeal
- Use markdown formatting (headers, lists, bold, tables)
- Be specific with ALL numbers, prices, and data
- Always respond in the same language as the user's query
- Make it actionable and professional
- Preserve ALL detailed information from the analyses"""

        final_messages = [
            SystemMessage(content="You are an expert business consultant creating executive reports."),
            HumanMessage(content=final_report_prompt),
        ]

        final_response = self.llm.invoke(final_messages)

        return {
            "final_report": final_response.content
        }

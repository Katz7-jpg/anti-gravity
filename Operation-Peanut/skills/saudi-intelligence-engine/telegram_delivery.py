#!/usr/bin/env python3
"""
Saudi Intelligence Engine - Extraction Pipeline
GOD-LEVEL B2B Lead Discovery + Bottleneck Intelligence
"""

import os
import json
import requests
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import aiohttp

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8570166186:AAHkGzrk42DebKCpo4WVIh5Hd2BRsodNQPQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6028670283")

class Tier(Enum):
    S = "S"  # Maximum Leverage
    A = "A"  # Strategic Platforms
    B = "B"  # Supporting Infrastructure

class AISolvability(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class Lead:
    """Person lead data structure"""
    name: str
    role: str
    company: str
    sector: str
    bottleneck_insight: str
    ai_solvability: AISolvability
    value_insight: str
    profile_link: str
    tier: Tier = Tier.S
    score: int = 0
    role_authority: int = 0
    multi_project_influence: int = 0
    sector_impact: int = 0
    economic_impact: int = 0
    ai_solvability_score: int = 0

@dataclass
class Company:
    """Company intelligence data structure"""
    name: str
    sector: str
    bottleneck_insight: Optional[str]
    ai_solvability: AISolvability
    relevance: str
    page_link: str
    tier: Tier = Tier.S
    score: int = 0

class ScoringEngine:
    """5-Factor Weighted Scoring System"""
    
    ROLE_SCORES = {
        "CEO": 20, "President": 20, "Managing Director": 20,
        "VP": 18, "SVP": 18, "Vice President": 18,
        "Director": 16, "Head of": 16,
        "Senior Manager": 14, "Manager": 12,
        "Senior Engineer": 10, "Lead": 8, "Principal": 8,
        "Engineer": 5, "Analyst": 5
    }
    
    TIER_SCORES = {Tier.S: 20, Tier.A: 15, Tier.B: 10}
    
    IMPACT_SCORES = {
        "multi_million_loss": 30,
        "major_delay": 25,
        "operational_inefficiency": 20,
        "compliance_gap": 15,
        "process_improvement": 10
    }
    
    SOLVABILITY_SCORES = {
        AISolvability.HIGH: 10,
        AISolvability.MEDIUM: 6,
        AISolvability.LOW: 2
    }
    
    @classmethod
    def calculate_lead_score(cls, lead: Lead) -> int:
        """Calculate comprehensive lead score"""
        score = 0
        
        # Factor 1: Role Authority (20 points max)
        role_score = 5
        for role_key, points in cls.ROLE_SCORES.items():
            if role_key.lower() in lead.role.lower():
                role_score = points
                break
        lead.role_authority = role_score
        score += role_score
        
        # Factor 2: Multi-Project Influence (20 points max)
        # Default to 10 if not specified
        lead.multi_project_influence = 10
        score += lead.multi_project_influence
        
        # Factor 3: Sector Impact (20 points max)
        lead.sector_impact = cls.TIER_SCORES.get(lead.tier, 10)
        score += lead.sector_impact
        
        # Factor 4: Economic Impact (30 points max)
        lead.economic_impact = cls.IMPACT_SCORES.get(
            cls._classify_bottleneck(lead.bottleneck_insight), 15
        )
        score += lead.economic_impact
        
        # Factor 5: AI Solvability (10 points max)
        lead.ai_solvability_score = cls.SOLVABILITY_SCORES.get(lead.ai_solvability, 2)
        score += lead.ai_solvability_score
        
        lead.score = score
        return score
    
    @classmethod
    def _classify_bottleneck(cls, insight: str) -> str:
        """Classify bottleneck type from insight text"""
        insight_lower = insight.lower()
        
        if any(kw in insight_lower for kw in ["million", "loss", "waste", "revenue"]):
            return "multi_million_loss"
        elif any(kw in insight_lower for kw in ["delay", "late", "schedule", "deadline"]):
            return "major_delay"
        elif any(kw in insight_lower for kw in ["inefficiency", "manual", "process", "productivity"]):
            return "operational_inefficiency"
        elif any(kw in insight_lower for kw in ["compliance", "regulatory", "audit", "penalty"]):
            return "compliance_gap"
        else:
            return "process_improvement"

class TelegramDelivery:
    """Telegram message delivery system"""
    
    API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    @classmethod
    async def send_message(cls, text: str, parse_mode: str = "Markdown") -> bool:
        """Send message to configured chat"""
        url = f"{cls.API_BASE}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return True
                else:
                    error = await response.text()
                    print(f"Telegram error: {error}")
                    return False
    
    @classmethod
    def format_lead(cls, lead: Lead) -> str:
        """Format lead for Telegram delivery"""
        tier_emoji = {"S": "🔥", "A": "⚡", "B": "📌"}
        emoji = tier_emoji.get(lead.tier.value, "🔹")
        
        return f"""{emoji} **Tier {lead.tier.value}** — High-Impact Lead

**Name:** {lead.name}
**Role:** {lead.role}
**Company:** {lead.company}
**Sector:** {lead.sector}
**Bottleneck Insight:** {lead.bottleneck_insight}
**AI Solvability:** {lead.ai_solvability.value}
**Why This Person Matters:** {lead.value_insight}
**Score:** {lead.score}/100
**Profile:** {lead.profile_link}"""
    
    @classmethod
    def format_company(cls, company: Company) -> str:
        """Format company for Telegram delivery"""
        tier_emoji = {"S": "🏢", "A": "🏛️", "B": "🏬"}
        emoji = tier_emoji.get(company.tier.value, "🏢")
        
        bottleneck_line = f"**Bottleneck Insight:** {company.bottleneck_insight}\n" if company.bottleneck_insight else ""
        
        return f"""{emoji} **Tier {company.tier.value}** — High-Impact Company

**Company:** {company.name}
**Sector:** {company.sector}
{bottleneck_line}**AI Solvability:** {company.ai_solvability.value}
**Why Follow:** {company.relevance}
**Link:** {company.page_link}"""
    
    @classmethod
    def format_summary(cls, leads: List[Lead], companies: List[Company]) -> str:
        """Format cycle summary"""
        tier_s_count = len([l for l in leads if l.tier == Tier.S])
        high_solvability = len([l for l in leads if l.ai_solvability == AISolvability.HIGH])
        
        return f"""📊 **Intelligence Cycle Summary**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Leads Extracted:** {len(leads)} people, {len(companies)} companies
**Tier S Opportunities:** {tier_s_count}
**High AI-Solvable Gaps:** {high_solvability}
**Sectors Covered:** Energy, Logistics, Industrial AI, Infrastructure
**Next Cycle:** {(datetime.now()).strftime('%Y-%m-%d')}"""

class QueryGenerator:
    """Generate search queries for intelligence extraction"""
    
    ROLE_TEMPLATES = [
        "Director of {function}",
        "VP of {function}",
        "Head of {function}",
        "Senior Manager {function}",
        "{role} Engineer"
    ]
    
    SECTORS = {
        Tier.S: [
            "Predictive Maintenance",
            "Industrial Automation",
            "Asset Management",
            "Supply Chain",
            "Operations"
        ],
        Tier.A: [
            "Digital Twin",
            "BIM",
            "Technology"
        ],
        Tier.B: [
            "Fintech",
            "Risk Analytics",
            "Compliance"
        ]
    }
    
    BOTTLENECK_KEYWORDS = [
        "bottleneck",
        "inefficiency",
        "challenge",
        "optimization",
        "automation gap",
        "manual process"
    ]
    
    @classmethod
    def generate_queries(cls, tier: Tier = Tier.S) -> List[str]:
        """Generate search queries for specified tier"""
        queries = []
        
        for sector in cls.SECTORS.get(tier, []):
            for keyword in cls.BOTTLENECK_KEYWORDS[:3]:  # Top 3 keywords
                query = f'"{sector}" "Saudi Arabia" "{keyword}"'
                queries.append(query)
        
        return queries

class IntelligenceEngine:
    """Main intelligence extraction engine"""
    
    def __init__(self):
        self.leads: List[Lead] = []
        self.companies: List[Company] = []
        self.scoring_engine = ScoringEngine()
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Execute full intelligence cycle"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "leads": [],
            "companies": [],
            "summary": {}
        }
        
        # Generate queries
        queries = QueryGenerator.generate_queries(Tier.S)
        queries.extend(QueryGenerator.generate_queries(Tier.A))
        
        # Score all leads
        for lead in self.leads:
            self.scoring_engine.calculate_lead_score(lead)
        
        # Filter by threshold
        qualified_leads = [l for l in self.leads if l.score >= 70]
        
        # Sort by score
        qualified_leads.sort(key=lambda x: x.score, reverse=True)
        
        # Limit to 10-20 leads
        qualified_leads = qualified_leads[:20]
        
        results["leads"] = qualified_leads
        results["companies"] = self.companies[:10]
        
        return results
    
    async def deliver_to_telegram(self, results: Dict[str, Any]) -> bool:
        """Deliver intelligence to Telegram"""
        # Send summary first
        summary = TelegramDelivery.format_summary(
            results["leads"], 
            results["companies"]
        )
        await TelegramDelivery.send_message(summary)
        
        # Send leads
        for lead in results["leads"]:
            message = TelegramDelivery.format_lead(lead)
            await TelegramDelivery.send_message(message)
            await asyncio.sleep(1)  # Rate limiting
        
        # Send companies
        for company in results["companies"]:
            message = TelegramDelivery.format_company(company)
            await TelegramDelivery.send_message(message)
            await asyncio.sleep(1)
        
        return True

# Example usage and testing
async def main():
    """Test the intelligence engine"""
    engine = IntelligenceEngine()
    
    # Add sample leads for testing
    sample_leads = [
        Lead(
            name="Ahmed Al-Rashid",
            role="Director of Operations",
            company="Saudi Aramco",
            sector="Energy & Industrial",
            bottleneck_insight="Multi-million dollar equipment downtime due to reactive maintenance",
            ai_solvability=AISolvability.HIGH,
            value_insight="Oversees predictive maintenance transformation initiative",
            profile_link="linkedin.com/in/example",
            tier=Tier.S
        ),
        Lead(
            name="Sarah Al-Fahad",
            role="VP Supply Chain",
            company="NEOM",
            sector="Logistics",
            bottleneck_insight="Supply chain visibility gaps causing project delays",
            ai_solvability=AISolvability.HIGH,
            value_insight="Leading digital transformation of NEOM logistics",
            profile_link="linkedin.com/in/example2",
            tier=Tier.S
        )
    ]
    
    engine.leads = sample_leads
    
    # Run cycle
    results = await engine.run_cycle()
    
    # Deliver
    await engine.deliver_to_telegram(results)
    
    print(f"Intelligence cycle complete. Delivered {len(results['leads'])} leads.")

if __name__ == "__main__":
    asyncio.run(main())

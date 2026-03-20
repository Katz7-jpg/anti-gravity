#!/usr/bin/env python3
"""
Saudi Intelligence Engine - Quick Run Script
Execute a single intelligence cycle and deliver to Telegram
Using requests library for better Windows compatibility
"""

import os
import sys
import requests
from datetime import datetime

# Add skill to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_delivery import (
    Lead, Company, Tier, AISolvability,
    ScoringEngine, IntelligenceEngine
)

# Configuration
TELEGRAM_BOT_TOKEN = "8570166186:AAHkGzrk42DebKCpo4WVIh5Hd2BRsodNQPQ"
TELEGRAM_CHAT_ID = "6028670283"
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_telegram_message(text: str, parse_mode: str = "Markdown") -> bool:
    """Send message to Telegram using requests library"""
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Request error: {e}")
        return False

def format_lead(lead) -> str:
    """Format lead for Telegram delivery"""
    tier_emoji = {"S": "🔥", "A": "⚡", "B": "📌"}
    emoji = tier_emoji.get(lead.tier.value, "🔹")
    
    return f"""{emoji} *Tier {lead.tier.value}* — High-Impact Lead

*Name:* {lead.name}
*Role:* {lead.role}
*Company:* {lead.company}
*Sector:* {lead.sector}
*Bottleneck Insight:* {lead.bottleneck_insight}
*AI Solvability:* {lead.ai_solvability.value}
*Why This Person Matters:* {lead.value_insight}
*Score:* {lead.score}/100
*Profile:* {lead.profile_link}"""

def format_company(company) -> str:
    """Format company for Telegram delivery"""
    tier_emoji = {"S": "🏢", "A": "🏛️", "B": "🏬"}
    emoji = tier_emoji.get(company.tier.value, "🏢")
    
    bottleneck_line = f"*Bottleneck Insight:* {company.bottleneck_insight}\n" if company.bottleneck_insight else ""
    
    return f"""{emoji} *Tier {company.tier.value}* — High-Impact Company

*Company:* {company.name}
*Sector:* {company.sector}
{bottleneck_line}*AI Solvability:* {company.ai_solvability.value}
*Why Follow:* {company.relevance}
*Link:* {company.page_link}"""

def format_summary(leads, companies) -> str:
    """Format cycle summary"""
    tier_s_count = len([l for l in leads if l.tier == Tier.S])
    high_solvability = len([l for l in leads if l.ai_solvability == AISolvability.HIGH])
    
    return f"""📊 *Intelligence Cycle Summary*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Leads Extracted:* {len(leads)} people, {len(companies)} companies
*Tier S Opportunities:* {tier_s_count}
*High AI-Solvable Gaps:* {high_solvability}
*Sectors Covered:* Energy, Logistics, Industrial AI, Infrastructure
*Next Cycle:* {datetime.now().strftime('%Y-%m-%d')}"""

def test_telegram_delivery():
    """Test Telegram delivery with sample intelligence"""
    
    # Create sample leads
    sample_leads = [
        Lead(
            name="Ahmed Al-Rashid",
            role="Director of Operations",
            company="Saudi Aramco",
            sector="Energy & Industrial",
            bottleneck_insight="Multi-million dollar equipment downtime due to reactive maintenance practices",
            ai_solvability=AISolvability.HIGH,
            value_insight="Oversees predictive maintenance transformation - direct decision authority",
            profile_link="linkedin.com/in/ahmed-al-rashid-aramco",
            tier=Tier.S
        ),
        Lead(
            name="Fatima Al-Zahrani",
            role="VP Supply Chain",
            company="NEOM",
            sector="Logistics & Supply Chain",
            bottleneck_insight="Supply chain visibility gaps causing 15% project delays",
            ai_solvability=AISolvability.HIGH,
            value_insight="Leading $2B logistics transformation - key technology buyer",
            profile_link="linkedin.com/in/fatima-al-zahrani-neom",
            tier=Tier.S
        ),
        Lead(
            name="Mohammed Al-Qasim",
            role="Head of Digital Transformation",
            company="SABIC",
            sector="Industrial AI",
            bottleneck_insight="Data silos preventing predictive analytics deployment",
            ai_solvability=AISolvability.HIGH,
            value_insight="Championing AI adoption across 60+ facilities",
            profile_link="linkedin.com/in/mohammed-al-qasim-sabic",
            tier=Tier.S
        ),
        Lead(
            name="Sarah Al-Fahad",
            role="Senior Manager Asset Management",
            company="Ma'aden",
            sector="Energy & Industrial",
            bottleneck_insight="Equipment tracking inefficiencies causing $5M annual losses",
            ai_solvability=AISolvability.HIGH,
            value_insight="Evaluating IoT solutions for 10,000+ assets",
            profile_link="linkedin.com/in/sarah-al-fahad-maaden",
            tier=Tier.S
        ),
        Lead(
            name="Khalid Al-Otaibi",
            role="Director of Maintenance",
            company="Saudi Electricity Company",
            sector="Energy & Industrial",
            bottleneck_insight="Preventive maintenance scheduling causing 20% overtime costs",
            ai_solvability=AISolvability.HIGH,
            value_insight="Managing maintenance for 50+ power plants",
            profile_link="linkedin.com/in/khalid-al-otaibi-sec",
            tier=Tier.S
        ),
    ]
    
    # Create sample companies
    sample_companies = [
        Company(
            name="Saudi Aramco",
            sector="Energy & Industrial",
            bottleneck_insight="Predictive maintenance gap - $500M+ annual downtime losses",
            ai_solvability=AISolvability.HIGH,
            relevance="World's largest oil company - massive AI adoption potential",
            page_link="https://www.aramco.com",
            tier=Tier.S
        ),
        Company(
            name="NEOM",
            sector="Industrial AI",
            bottleneck_insight="Digital twin integration challenges across mega-projects",
            ai_solvability=AISolvability.HIGH,
            relevance="$500B mega-project - technology-first approach",
            page_link="https://www.neom.com",
            tier=Tier.S
        ),
        Company(
            name="SABIC",
            sector="Industrial AI",
            bottleneck_insight="Process optimization opportunities across chemical plants",
            ai_solvability=AISolvability.HIGH,
            relevance="World's 4th largest chemical company",
            page_link="https://www.sabic.com",
            tier=Tier.S
        ),
        Company(
            name="Ma'aden",
            sector="Energy & Industrial",
            bottleneck_insight="Mining operations automation gaps",
            ai_solvability=AISolvability.HIGH,
            relevance="Saudi's mining champion - $20B+ investments",
            page_link="https://www.maaden.com.sa",
            tier=Tier.S
        ),
        Company(
            name="ACWA Power",
            sector="Energy & Industrial",
            bottleneck_insight="Renewable energy asset monitoring opportunities",
            ai_solvability=AISolvability.HIGH,
            relevance="Leading desalination and power company",
            page_link="https://www.acwapower.com",
            tier=Tier.A
        ),
    ]
    
    # Score leads
    for lead in sample_leads:
        ScoringEngine.calculate_lead_score(lead)
        print(f"Scored {lead.name}: {lead.score}/100")
    
    # Filter qualified leads
    qualified_leads = [l for l in sample_leads if l.score >= 70]
    qualified_leads.sort(key=lambda x: x.score, reverse=True)
    
    print(f"\n✅ {len(qualified_leads)} qualified leads (score ≥ 70)")
    
    # Deliver to Telegram
    print("\n📤 Delivering to Telegram...")
    
    # Send summary
    summary = format_summary(qualified_leads, sample_companies)
    success = send_telegram_message(summary)
    
    if success:
        print("✅ Summary sent")
    else:
        print("❌ Summary failed")
        return False
    
    # Send leads
    import time
    for i, lead in enumerate(qualified_leads, 1):
        message = format_lead(lead)
        success = send_telegram_message(message)
        if success:
            print(f"✅ Lead {i}/{len(qualified_leads)} sent: {lead.name}")
        else:
            print(f"❌ Lead {i} failed")
        time.sleep(1)  # Rate limiting
    
    # Send companies
    for i, company in enumerate(sample_companies, 1):
        message = format_company(company)
        success = send_telegram_message(message)
        if success:
            print(f"✅ Company {i}/{len(sample_companies)} sent: {company.name}")
        else:
            print(f"❌ Company {i} failed")
        time.sleep(1)
    
    return True

def main():
    """Main entry point"""
    print("=" * 60)
    print("🇸🇦 SAUDI INTELLIGENCE ENGINE - TEST CYCLE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Chat ID: {TELEGRAM_CHAT_ID}")
    print("=" * 60)
    print()
    
    success = test_telegram_delivery()
    
    print()
    print("=" * 60)
    if success:
        print("✅ INTELLIGENCE CYCLE COMPLETE")
        print("Check your Telegram for the delivered intelligence!")
    else:
        print("❌ INTELLIGENCE CYCLE FAILED")
        print("Check the error messages above")
    print("=" * 60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Saudi Intelligence Engine - Web Extraction Module
GOD-LEVEL Intelligence Extraction using Exa Search API
"""

import os
import json
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

# Import from telegram_delivery
from telegram_delivery import (
    Lead, Company, Tier, AISolvability, 
    ScoringEngine, TelegramDelivery, IntelligenceEngine
)

# Exa API Configuration
EXA_API_KEY = os.getenv("EXA_API_KEY", "")
EXA_API_URL = "https://api.exa.ai/search"

class ExaSearchClient:
    """Exa AI Search Client for intelligence extraction"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or EXA_API_KEY
        self.base_url = EXA_API_URL
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Execute search query via Exa API"""
        import aiohttp
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        payload = {
            "query": query,
            "numResults": num_results,
            "useAutoprompt": True,
            "type": "auto",
            "contents": {
                "text": {
                    "maxCharacters": 2000
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    print(f"Exa API error: {response.status}")
                    return []
    
    async def search_linkedin_profiles(self, role: str, company: str = None, sector: str = None) -> List[Dict]:
        """Search for LinkedIn profiles"""
        query = f'site:linkedin.com/in "{role}"'
        if company:
            query += f' "{company}"'
        if sector:
            query += f' "{sector}"'
        query += ' Saudi Arabia -job -apply -hiring'
        
        return await self.search(query, num_results=15)
    
    async def search_company_intelligence(self, company: str, sector: str = None) -> List[Dict]:
        """Search for company intelligence"""
        query = f'"{company}"'
        if sector:
            query += f' "{sector}"'
        query += ' Saudi Arabia leadership team management'
        
        return await self.search(query, num_results=10)

class LeadExtractor:
    """Extract leads from search results"""
    
    # Role patterns for extraction
    ROLE_PATTERNS = [
        r"(CEO|Chief Executive Officer)",
        r"(VP|Vice President)\s+of\s+(\w+)",
        r"(Director)\s+of\s+(\w+)",
        r"(Head)\s+of\s+(\w+)",
        r"(Senior\s+Manager)\s+(\w+)",
        r"(Manager)\s+(\w+)",
        r"(Senior\s+Engineer)\s+(\w+)",
        r"(Lead\s+Engineer)\s+(\w+)",
    ]
    
    # Company patterns
    COMPANY_PATTERNS = [
        r"(Saudi\s+Aramco|Aramco)",
        r"(NEOM)",
        r"(SABIC)",
        r"(PIF|Public\s+Investment\s+Fund)",
        r"(Saudi\s+Electricity\s+Company|SEC)",
        r"(ACWA\s+Power)",
        r"(Ma'aden)",
        r"(STC|Saudi\s+Telecom)",
    ]
    
    @classmethod
    def extract_from_result(cls, result: Dict) -> Optional[Lead]:
        """Extract lead from search result"""
        text = result.get("text", "")
        url = result.get("url", "")
        title = result.get("title", "")
        
        # Extract name from title (LinkedIn format: "Name - Role - Company")
        name = cls._extract_name(title)
        if not name:
            return None
        
        # Extract role
        role = cls._extract_role(title + " " + text)
        if not role:
            return None
        
        # Extract company
        company = cls._extract_company(title + " " + text)
        if not company:
            company = "Unknown"
        
        # Determine sector
        sector = cls._determine_sector(text)
        
        # Determine tier
        tier = cls._determine_tier(role, company, sector)
        
        # Extract bottleneck insight
        bottleneck = cls._extract_bottleneck(text)
        
        # Determine AI solvability
        ai_solvability = cls._determine_ai_solvability(bottleneck)
        
        return Lead(
            name=name,
            role=role,
            company=company,
            sector=sector,
            bottleneck_insight=bottleneck,
            ai_solvability=ai_solvability,
            value_insight=f"Key decision-maker in {sector}",
            profile_link=url,
            tier=tier
        )
    
    @classmethod
    def _extract_name(cls, text: str) -> Optional[str]:
        """Extract person name from text"""
        # LinkedIn title format: "Name - Role - Company"
        parts = text.split(" - ")
        if parts:
            name = parts[0].strip()
            # Validate it looks like a name
            if len(name.split()) >= 2 and len(name) < 50:
                return name
        return None
    
    @classmethod
    def _extract_role(cls, text: str) -> Optional[str]:
        """Extract role from text"""
        for pattern in cls.ROLE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    @classmethod
    def _extract_company(cls, text: str) -> Optional[str]:
        """Extract company from text"""
        for pattern in cls.COMPANY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    @classmethod
    def _determine_sector(cls, text: str) -> str:
        """Determine sector from text"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["oil", "gas", "energy", "aramco", "refinery"]):
            return "Energy & Industrial"
        elif any(kw in text_lower for kw in ["logistics", "supply chain", "port", "warehouse"]):
            return "Logistics & Supply Chain"
        elif any(kw in text_lower for kw in ["ai", "digital", "technology", "automation"]):
            return "Industrial AI"
        elif any(kw in text_lower for kw in ["construction", "real estate", "bim"]):
            return "Construction & Real Estate"
        elif any(kw in text_lower for kw in ["fintech", "banking", "payment"]):
            return "Financial Infrastructure"
        else:
            return "Industrial"
    
    @classmethod
    def _determine_tier(cls, role: str, company: str, sector: str) -> Tier:
        """Determine tier based on role, company, sector"""
        # Tier S conditions
        tier_s_sectors = ["Energy & Industrial", "Logistics & Supply Chain", "Industrial AI"]
        tier_s_roles = ["CEO", "VP", "Director", "Head of"]
        tier_s_companies = ["Aramco", "NEOM", "SABIC", "PIF"]
        
        if any(c in company for c in tier_s_companies):
            return Tier.S
        if sector in tier_s_sectors and any(r in role for r in tier_s_roles):
            return Tier.S
        
        # Tier A conditions
        tier_a_sectors = ["Construction & Real Estate"]
        tier_a_roles = ["Senior Manager", "Manager"]
        
        if sector in tier_a_sectors or any(r in role for r in tier_a_roles):
            return Tier.A
        
        return Tier.B
    
    @classmethod
    def _extract_bottleneck(cls, text: str) -> str:
        """Extract bottleneck insight from text"""
        bottleneck_keywords = [
            "inefficiency", "bottleneck", "challenge", "delay",
            "manual process", "automation gap", "optimization",
            "downtime", "waste", "cost"
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in bottleneck_keywords if kw in text_lower]
        
        if found_keywords:
            return f"Identified operational {found_keywords[0]} requiring attention"
        
        return "Potential operational improvement opportunity"
    
    @classmethod
    def _determine_ai_solvability(cls, bottleneck: str) -> AISolvability:
        """Determine AI solvability based on bottleneck"""
        high_solvability_keywords = [
            "automation", "predictive", "scheduling", "reporting",
            "tracking", "monitoring", "optimization"
        ]
        
        bottleneck_lower = bottleneck.lower()
        
        if any(kw in bottleneck_lower for kw in high_solvability_keywords):
            return AISolvability.HIGH
        elif "process" in bottleneck_lower or "efficiency" in bottleneck_lower:
            return AISolvability.MEDIUM
        
        return AISolvability.MEDIUM

class CompanyExtractor:
    """Extract company intelligence from search results"""
    
    @classmethod
    def extract_from_result(cls, result: Dict, sector: str) -> Optional[Company]:
        """Extract company from search result"""
        text = result.get("text", "")
        url = result.get("url", "")
        title = result.get("title", "")
        
        # Extract company name
        name = cls._extract_company_name(title, text)
        if not name:
            return None
        
        # Determine tier
        tier = cls._determine_tier(name, sector)
        
        # Extract bottleneck
        bottleneck = cls._extract_bottleneck(text)
        
        # Determine AI solvability
        ai_solvability = AISolvability.HIGH if tier == Tier.S else AISolvability.MEDIUM
        
        return Company(
            name=name,
            sector=sector,
            bottleneck_insight=bottleneck,
            ai_solvability=ai_solvability,
            relevance=f"Key player in Saudi {sector}",
            page_link=url,
            tier=tier
        )
    
    @classmethod
    def _extract_company_name(cls, title: str, text: str) -> Optional[str]:
        """Extract company name"""
        # Common Saudi companies
        companies = [
            "Saudi Aramco", "Aramco", "NEOM", "SABIC", 
            "Saudi Electricity Company", "SEC", "ACWA Power",
            "Ma'aden", "STC", "Saudi Telecom", "Bahri",
            "ROSHN", "Diriyah Gate", "Red Sea Global", "Qiddiya"
        ]
        
        combined = title + " " + text
        for company in companies:
            if company.lower() in combined.lower():
                return company
        
        # Try to extract from title
        parts = title.split(" - ")
        if len(parts) >= 2:
            return parts[-1].strip()
        
        return None
    
    @classmethod
    def _determine_tier(cls, name: str, sector: str) -> Tier:
        """Determine company tier"""
        tier_s_companies = ["Aramco", "NEOM", "SABIC", "PIF", "Ma'aden"]
        tier_a_companies = ["ACWA", "SEC", "STC", "ROSHN", "Red Sea"]
        
        if any(c in name for c in tier_s_companies):
            return Tier.S
        if any(c in name for c in tier_a_companies):
            return Tier.A
        return Tier.B
    
    @classmethod
    def _extract_bottleneck(cls, text: str) -> str:
        """Extract company bottleneck"""
        # Similar to lead bottleneck extraction
        return "Operational efficiency opportunities identified"

class FullIntelligencePipeline:
    """Complete intelligence extraction pipeline"""
    
    def __init__(self, exa_api_key: str = None):
        self.search_client = ExaSearchClient(exa_api_key)
        self.leads: List[Lead] = []
        self.companies: List[Company] = []
    
    async def run_full_extraction(self) -> Dict[str, Any]:
        """Run complete intelligence extraction cycle"""
        
        # Define search queries by priority
        queries = [
            # Tier S - Energy & Industrial
            ('"Predictive Maintenance" "Saudi Aramco" engineer manager director',
             "Energy & Industrial"),
            ('"Industrial Automation" "Saudi" director manager',
             "Industrial AI"),
            ('"Supply Chain Director" "Riyadh" "Saudi Arabia"',
             "Logistics & Supply Chain"),
            
            # Tier S - NEOM
            ('"NEOM" "Director" "Operations" "Engineering"',
             "Industrial AI"),
            ('"Digital Twin" "NEOM" "Saudi" engineer',
             "Industrial AI"),
            
            # Tier A - Construction
            ('"BIM Manager" "Saudi Arabia" construction',
             "Construction & Real Estate"),
            ('"Project Director" "mega project" "Saudi"',
             "Construction & Real Estate"),
            
            # Boring but Lucrative
            ('"Asset Management" "Saudi" "equipment tracking"',
             "Industrial AI"),
            ('"Compliance Manager" "Saudi Arabia" regulatory',
             "Financial Infrastructure"),
        ]
        
        all_results = []
        
        # Execute searches
        for query, sector in queries:
            print(f"Searching: {query}")
            results = await self.search_client.search(query, num_results=10)
            
            for result in results:
                result["_sector"] = sector
                all_results.append(result)
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Extract leads
        for result in all_results:
            lead = LeadExtractor.extract_from_result(result)
            if lead:
                self.leads.append(lead)
        
        # Extract companies
        for result in all_results:
            company = CompanyExtractor.extract_from_result(
                result, result.get("_sector", "Industrial")
            )
            if company:
                # Avoid duplicates
                if not any(c.name == company.name for c in self.companies):
                    self.companies.append(company)
        
        # Score all leads
        for lead in self.leads:
            ScoringEngine.calculate_lead_score(lead)
        
        # Filter and sort
        qualified_leads = [l for l in self.leads if l.score >= 70]
        qualified_leads.sort(key=lambda x: x.score, reverse=True)
        
        # Remove duplicates by name
        seen_names = set()
        unique_leads = []
        for lead in qualified_leads:
            if lead.name not in seen_names:
                seen_names.add(lead.name)
                unique_leads.append(lead)
        
        # Limit to 10-20 leads, 5-10 companies
        final_leads = unique_leads[:20]
        final_companies = self.companies[:10]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "leads": final_leads,
            "companies": final_companies,
            "summary": {
                "total_extracted": len(self.leads),
                "qualified": len(qualified_leads),
                "delivered": len(final_leads)
            }
        }
    
    async def deliver_results(self, results: Dict[str, Any]) -> bool:
        """Deliver results to Telegram"""
        engine = IntelligenceEngine()
        engine.leads = results["leads"]
        engine.companies = results["companies"]
        
        return await engine.deliver_to_telegram(results)

# CLI Entry Point
async def main():
    """Main execution function"""
    print("=" * 50)
    print("Saudi Intelligence Engine - Starting Cycle")
    print("=" * 50)
    
    pipeline = FullIntelligencePipeline()
    
    # Run extraction
    results = await pipeline.run_full_extraction()
    
    print(f"\nExtracted {results['summary']['total_extracted']} leads")
    print(f"Qualified: {results['summary']['qualified']}")
    print(f"Delivering: {results['summary']['delivered']}")
    
    # Deliver to Telegram
    await pipeline.deliver_results(results)
    
    print("\n✅ Intelligence cycle complete!")
    print(f"Delivered to Telegram Chat ID: {os.getenv('TELEGRAM_CHAT_ID', '6028670283')}")

if __name__ == "__main__":
    asyncio.run(main())

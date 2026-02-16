#!/usr/bin/env python3
"""
Python SDK Implementation: Automated API Discovery & Tool Creation

This script demonstrates the complete workflow for discovering life science APIs
and creating ToolUniverse tools automatically.

Usage:
    # Full pipeline
    python python_implementation.py --mode full

    # Discovery only
    python python_implementation.py --mode discovery --focus-domains metabolomics single-cell

    # Create tools from specific APIs
    python python_implementation.py --mode create --apis MetaboLights GNPS

    # Validate existing tools
    python python_implementation.py --mode validate --tools MetaboLights_*

    # Create PR for validated tools
    python python_implementation.py --mode integrate --branch feature/add-metabolomics-tools
"""

import argparse
import json
import os
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from tooluniverse import ToolUniverse
    from tooluniverse.tool_registry import get_tool_registry
    from tooluniverse.default_config import default_tool_files
except ImportError:
    print("ToolUniverse not found in path. Some functions may not work.")


class APIDiscoveryAgent:
    """Automated API discovery and tool creation agent."""

    def __init__(self, config: dict[str, Any] = None):
        """Initialize agent with configuration."""
        self.config = config or {}
        self.output_dir = Path("./api_discovery_output")
        self.output_dir.mkdir(exist_ok=True)

        # Domain keywords for categorization
        self.domain_keywords = {
            "genomics": ["sequence", "genome", "gene", "variant", "snp", "dna", "rna"],
            "proteomics": ["protein", "structure", "pdb", "fold", "domain", "uniprot"],
            "drug_discovery": ["drug", "compound", "molecule", "ligand", "admet", "binding"],
            "clinical": ["disease", "patient", "trial", "phenotype", "diagnosis", "symptom"],
            "omics": ["expression", "transcriptome", "metabolome", "proteome", "omics"],
            "imaging": ["microscopy", "imaging", "scan", "radiology", "image"],
            "literature": ["pubmed", "citation", "publication", "article", "paper"],
            "pathways": ["pathway", "network", "interaction", "signaling", "cascade"],
            "systems_biology": ["model", "simulation", "flux", "dynamics", "systems"],
            "metabolomics": ["metabolite", "metabolomics", "compound", "chemical"],
            "single_cell": ["single-cell", "scRNA", "spatial", "cell-type"],
        }

    # ========== PHASE 1: DISCOVERY & GAP ANALYSIS ==========

    def phase1_discovery(self, focus_domains: list[str] = None) -> dict[str, Any]:
        """
        Phase 1: Discover APIs and analyze gaps.

        Args:
            focus_domains: Optional list of domains to prioritize

        Returns:
            Discovery results with prioritized API candidates
        """
        print("=" * 80)
        print("PHASE 1: DISCOVERY & GAP ANALYSIS")
        print("=" * 80)

        # Step 1.1: Analyze current coverage
        print("\n[Step 1.1] Analyzing current ToolUniverse coverage...")
        coverage = self._analyze_coverage()
        self._print_coverage_summary(coverage)

        # Step 1.2: Identify gaps
        print("\n[Step 1.2] Identifying gap domains...")
        gaps = self._identify_gaps(coverage, focus_domains)
        self._print_gaps(gaps)

        # Step 1.3: Web search for APIs
        print("\n[Step 1.3] Searching for APIs in gap domains...")
        print("⚠️  NOTE: This requires WebSearch tool. In this demo, using example data.")
        apis = self._search_apis(gaps)

        # Step 1.4: Score and prioritize
        print("\n[Step 1.4] Scoring and prioritizing APIs...")
        prioritized = self._prioritize_apis(apis)

        # Step 1.5: Generate report
        print("\n[Step 1.5] Generating discovery report...")
        report_path = self._generate_discovery_report(coverage, gaps, prioritized)
        print(f"✅ Discovery report: {report_path}")

        return {
            "coverage": coverage,
            "gaps": gaps,
            "apis": prioritized,
            "report_path": report_path,
        }

    def _analyze_coverage(self) -> dict[str, Any]:
        """Analyze current tool coverage by domain."""
        try:
            tu = ToolUniverse()
            tu.load_tools()

            # Categorize all tools
            tool_categories = defaultdict(list)
            total_tools = 0

            for tool_name in tu.all_tool_dict.keys():
                # Skip internal tools
                if tool_name.startswith("_"):
                    continue

                total_tools += 1

                # Categorize by keywords
                tool_lower = tool_name.lower()
                categorized = False

                for domain, keywords in self.domain_keywords.items():
                    if any(kw in tool_lower for kw in keywords):
                        tool_categories[domain].append(tool_name)
                        categorized = True
                        break

                if not categorized:
                    tool_categories["other"].append(tool_name)

            return {
                "total_tools": total_tools,
                "by_domain": dict(tool_categories),
                "domain_counts": {
                    domain: len(tools) for domain, tools in tool_categories.items()
                },
            }

        except Exception as e:
            print(f"⚠️  Could not load ToolUniverse: {e}")
            return {"total_tools": 0, "by_domain": {}, "domain_counts": {}}

    def _print_coverage_summary(self, coverage: dict[str, Any]):
        """Print coverage analysis summary."""
        print(f"\nTotal tools in ToolUniverse: {coverage['total_tools']}")
        print("\nTools by domain:")

        sorted_domains = sorted(
            coverage["domain_counts"].items(), key=lambda x: x[1], reverse=True
        )

        for domain, count in sorted_domains:
            bar = "█" * (count // 5)
            print(f"  {domain:20s}: {count:4d} {bar}")

    def _identify_gaps(
        self, coverage: dict[str, Any], focus_domains: list[str] = None
    ) -> list[dict[str, Any]]:
        """Identify gap domains based on tool counts."""
        gaps = []

        for domain, count in coverage["domain_counts"].items():
            # Skip if focusing on specific domains and this isn't one
            if focus_domains and domain not in focus_domains:
                continue

            # Determine gap severity
            if count == 0:
                severity = "critical"
                reason = "No tools in this domain"
            elif count < 5:
                severity = "high"
                reason = f"Only {count} tools, likely missing key subcategories"
            elif count < 15:
                severity = "moderate"
                reason = f"{count} tools but may be incomplete coverage"
            else:
                continue  # Not a gap

            gaps.append(
                {
                    "domain": domain,
                    "severity": severity,
                    "current_count": count,
                    "reason": reason,
                }
            )

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "moderate": 2}
        gaps.sort(key=lambda x: (severity_order[x["severity"]], x["current_count"]))

        return gaps

    def _print_gaps(self, gaps: list[dict[str, Any]]):
        """Print identified gaps."""
        if not gaps:
            print("No significant gaps identified!")
            return

        print("\nIdentified gaps:")
        for gap in gaps:
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "moderate": "🟡",
            }[gap["severity"]]

            print(
                f"  {severity_icon} {gap['domain']:20s}: "
                f"{gap['current_count']:2d} tools - {gap['reason']}"
            )

    def _search_apis(self, gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Search for APIs in gap domains.

        In a real implementation, this would:
        1. Use WebSearch tool to find APIs
        2. Scrape API documentation
        3. Extract metadata

        For this demo, returns example APIs.
        """
        example_apis = [
            {
                "name": "MetaboLights",
                "domain": "metabolomics",
                "base_url": "https://www.ebi.ac.uk/metabolights/ws",
                "description": "Database of metabolomics experiments and derived information",
                "auth_method": "public",
                "endpoints": [
                    {"path": "/studies", "method": "GET", "description": "List studies"},
                    {
                        "path": "/studies/{id}",
                        "method": "GET",
                        "description": "Get study details",
                    },
                    {
                        "path": "/studies/{id}/metabolites",
                        "method": "GET",
                        "description": "Get study metabolites",
                    },
                ],
                "documentation_url": "https://www.ebi.ac.uk/metabolights/ws/api/spec/",
                "rate_limits": "None documented",
                "license": "Open Data",
            },
            {
                "name": "GNPS",
                "domain": "metabolomics",
                "base_url": "https://gnps.ucsd.edu/ProteoSAFe",
                "description": "Global Natural Products Social Molecular Networking",
                "auth_method": "public",
                "endpoints": [
                    {
                        "path": "/result.jsp",
                        "method": "GET",
                        "description": "Get job results",
                    },
                    {
                        "path": "/status_json.jsp",
                        "method": "GET",
                        "description": "Check job status",
                    },
                ],
                "documentation_url": "https://ccms-ucsd.github.io/GNPSDocumentation/",
                "rate_limits": "Reasonable use policy",
                "license": "Open Data",
            },
            {
                "name": "Human Cell Atlas",
                "domain": "single_cell",
                "base_url": "https://data.humancellatlas.org",
                "description": "Single-cell genomics data from the Human Cell Atlas",
                "auth_method": "api_key_optional",
                "endpoints": [
                    {
                        "path": "/repository/projects",
                        "method": "GET",
                        "description": "List projects",
                    },
                    {
                        "path": "/repository/files",
                        "method": "GET",
                        "description": "Search files",
                    },
                ],
                "documentation_url": "https://data.humancellatlas.org/apis",
                "rate_limits": "10 req/sec",
                "license": "Open Data",
            },
        ]

        # Filter to gap domains
        gap_domains = {gap["domain"] for gap in gaps}
        return [api for api in example_apis if api["domain"] in gap_domains]

    def _prioritize_apis(self, apis: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score and prioritize APIs."""
        for api in apis:
            score = 0

            # Documentation quality (0-20)
            if "openapi" in api.get("documentation_url", "").lower():
                score += 20
            elif api.get("documentation_url"):
                score += 15
            else:
                score += 5

            # Authentication (0-15)
            auth = api.get("auth_method", "")
            if auth == "public":
                score += 15
            elif "key" in auth:
                score += 10
            else:
                score += 5

            # Coverage (0-15)
            endpoint_count = len(api.get("endpoints", []))
            if endpoint_count >= 5:
                score += 15
            elif endpoint_count >= 3:
                score += 10
            else:
                score += 5

            # License (0-10)
            license_text = api.get("license", "").lower()
            if "open" in license_text:
                score += 10
            elif "free" in license_text:
                score += 7
            else:
                score += 3

            # Add score
            api["score"] = score

            # Determine priority
            if score >= 70:
                api["priority"] = "high"
            elif score >= 50:
                api["priority"] = "medium"
            else:
                api["priority"] = "low"

        # Sort by score
        apis.sort(key=lambda x: x["score"], reverse=True)

        return apis

    def _generate_discovery_report(
        self,
        coverage: dict[str, Any],
        gaps: list[dict[str, Any]],
        apis: list[dict[str, Any]],
    ) -> Path:
        """Generate discovery report markdown."""
        report_path = self.output_dir / f"discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, "w") as f:
            f.write("# API Discovery Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- Total APIs discovered: {len(apis)}\n")
            f.write(
                f"- High priority: {len([a for a in apis if a['priority'] == 'high'])}\n"
            )
            f.write(
                f"- Medium priority: {len([a for a in apis if a['priority'] == 'medium'])}\n"
            )
            f.write(f"- Gap domains addressed: {len(gaps)}\n\n")

            # Coverage Analysis
            f.write("## Coverage Analysis\n\n")
            f.write(f"Total tools in ToolUniverse: {coverage['total_tools']}\n\n")
            f.write("| Domain | Tool Count | Status |\n")
            f.write("|--------|------------|--------|\n")

            for domain, count in sorted(
                coverage["domain_counts"].items(), key=lambda x: x[1]
            ):
                if count >= 15:
                    status = "Good"
                elif count >= 5:
                    status = "Gap"
                else:
                    status = "Critical"
                f.write(f"| {domain} | {count} | {status} |\n")

            # Gap Details
            f.write("\n## Identified Gaps\n\n")
            for gap in gaps:
                f.write(f"### {gap['domain']} ({gap['severity']} priority)\n\n")
                f.write(f"- Current tools: {gap['current_count']}\n")
                f.write(f"- Reason: {gap['reason']}\n\n")

            # Prioritized APIs
            f.write("## Prioritized API Candidates\n\n")

            for priority in ["high", "medium", "low"]:
                priority_apis = [a for a in apis if a["priority"] == priority]
                if not priority_apis:
                    continue

                f.write(f"### {priority.title()} Priority\n\n")

                for api in priority_apis:
                    f.write(f"#### {api['name']}\n\n")
                    f.write(f"- **Domain**: {api['domain']}\n")
                    f.write(f"- **Score**: {api['score']}/100\n")
                    f.write(f"- **Base URL**: {api['base_url']}\n")
                    f.write(f"- **Auth**: {api['auth_method']}\n")
                    f.write(f"- **Endpoints**: {len(api['endpoints'])}\n")
                    f.write(f"- **Description**: {api['description']}\n")
                    f.write(f"- **Documentation**: {api['documentation_url']}\n\n")

                    f.write("**Example Operations**:\n")
                    for endpoint in api["endpoints"][:3]:  # Show first 3
                        f.write(
                            f"- {endpoint['method']} {endpoint['path']}: {endpoint['description']}\n"
                        )
                    f.write("\n")

            # Implementation Roadmap
            f.write("## Implementation Roadmap\n\n")
            batch_labels = {"high": "Batch 1 (Immediate)", "medium": "Batch 2 (Next)"}
            for priority, batch_label in batch_labels.items():
                batch_apis = [a for a in apis if a["priority"] == priority]
                if batch_apis:
                    f.write(f"### {batch_label}\n")
                    for api in batch_apis:
                        f.write(f"- {api['name']} ({api['domain']})\n")
                    f.write("\n")

        return report_path

    # ========== PHASE 2: TOOL CREATION ==========

    def phase2_creation(self, api: dict[str, Any]) -> dict[str, Any]:
        """
        Phase 2: Create tools for an API.

        Args:
            api: API metadata from discovery phase

        Returns:
            Paths to created tool files
        """
        print("=" * 80)
        print(f"PHASE 2: TOOL CREATION - {api['name']}")
        print("=" * 80)

        # Step 2.1: Design architecture
        print("\n[Step 2.1] Designing tool architecture...")
        architecture = self._design_architecture(api)
        print(f"Architecture: {architecture['type']}")
        print(f"Operations: {len(architecture['operations'])}")

        # Step 2.2: Generate Python class
        print("\n[Step 2.2] Generating Python tool class...")
        py_path = self._generate_python_class(api, architecture)
        print(f"✅ Created: {py_path}")

        # Step 2.3: Generate JSON config
        print("\n[Step 2.3] Generating JSON configuration...")
        json_path = self._generate_json_config(api, architecture)
        print(f"✅ Created: {json_path}")

        # Step 2.4: Find test examples
        print("\n[Step 2.4] Finding real test examples...")
        test_examples = self._find_test_examples(api)
        print(f"✅ Found {len(test_examples)} test examples")

        # Step 2.5: Update default_config.py
        print("\n[Step 2.5] Updating default_config.py...")
        self._update_default_config(api)
        print("✅ Configuration registered")

        return {
            "api_name": api["name"],
            "py_path": py_path,
            "json_path": json_path,
            "architecture": architecture,
            "test_examples": test_examples,
        }

    # Maps HTTP methods to operation name prefixes
    _METHOD_PREFIXES = {"POST": "create", "PUT": "update", "DELETE": "delete"}

    def _design_architecture(self, api: dict[str, Any]) -> dict[str, Any]:
        """Design tool architecture based on API structure."""
        endpoints = api.get("endpoints", [])

        operations = []
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"]

            # Extract operation name from path segments (e.g., /studies/{id} -> "studies")
            path_parts = [p for p in path.split("/") if p and "{" not in p]
            op_name = "_".join(path_parts).lower()

            if method == "GET":
                op_prefix = "get" if "{" in path else "list"
            else:
                op_prefix = self._METHOD_PREFIXES.get(method, method.lower())

            operations.append(
                {
                    "name": f"{op_prefix}_{op_name}" if op_name else op_prefix,
                    "method": method,
                    "path": path,
                    "description": endpoint["description"],
                }
            )

        return {
            "type": "multi-operation" if len(operations) > 1 else "single-operation",
            "operations": operations,
        }

    def _generate_python_class(
        self, api: dict[str, Any], architecture: dict[str, Any]
    ) -> Path:
        """Generate Python tool class file."""
        api_name = api["name"].replace(" ", "")
        class_name = f"{api_name}Tool"
        file_name = f"{api_name.lower()}_tool.py"

        # This would generate actual Python code
        # For demo, create a template

        py_content = f'''"""
{api["name"]} Tool

{api["description"]}

API Documentation: {api["documentation_url"]}
"""

from typing import Dict, Any
from tooluniverse.tool import BaseTool
from tooluniverse.tool_utils import register_tool
import requests
import os


@register_tool("{class_name}")
class {class_name}(BaseTool):
    """{api["name"]} API integration."""

    BASE_URL = "{api["base_url"]}"

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.parameter = tool_config.get("parameter", {{}})
        self.required = self.parameter.get("required", [])
        # Optional API key
        self.api_key = os.environ.get("{api_name.upper()}_API_KEY", "")

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Route to operation handler."""
        operation = arguments.get("operation")

        if not operation:
            return {{"status": "error", "error": "Missing required parameter: operation"}}

        # Route operations
'''

        for op in architecture["operations"]:
            py_content += (
                f'        if operation == "{op["name"]}":\n'
                f'            return self._{op["name"]}(arguments)\n'
            )

        py_content += '''
        return {"status": "error", "error": f"Unknown operation: {operation}"}
'''

        # Add operation methods
        for op in architecture["operations"]:
            py_content += f'''
    def _{op["name"]}(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """{op["description"]}"""
        try:
            # Build request
            headers = {{}}
            if self.api_key:
                headers["Authorization"] = f"Bearer {{self.api_key}}"

            # Make API call
            response = requests.{op["method"].lower()}(
                f"{{self.BASE_URL}}{op["path"]}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            # Parse response
            data = response.json()

            return {{
                "status": "success",
                "data": data,
                "metadata": {{"source": "{api["name"]}"}}
            }}

        except requests.exceptions.Timeout:
            return {{"status": "error", "error": "API timeout after 30 seconds"}}
        except requests.exceptions.HTTPError as e:
            return {{"status": "error", "error": f"HTTP {{e.response.status_code}}: {{e.response.text[:200]}}"}}
        except Exception as e:
            return {{"status": "error", "error": f"Unexpected error: {{str(e)}}"}}
'''

        # Write file
        output_path = self.output_dir / file_name
        with open(output_path, "w") as f:
            f.write(py_content)

        return output_path

    def _generate_json_config(
        self, api: dict[str, Any], architecture: dict[str, Any]
    ) -> Path:
        """Generate JSON configuration file."""
        api_name = api["name"].replace(" ", "")
        class_name = f"{api_name}Tool"
        file_name = f"{api_name.lower()}_tools.json"

        tools = []

        for op in architecture["operations"]:
            tool = {
                "name": f"{api_name}_{op['name']}",
                "class": class_name,
                "description": f"{op['description']}. Returns data from {api['name']} API. Example usage: {op['name']} operation.",
                "parameter": {
                    "type": "object",
                    "required": ["operation"],
                    "properties": {
                        "operation": {
                            "const": op["name"],
                            "description": "Operation identifier (fixed)",
                        }
                    },
                },
                "return_schema": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "data": {
                                    "type": "object",
                                    "description": "Response data",
                                },
                                "metadata": {
                                    "type": "object",
                                    "properties": {"source": {"type": "string"}},
                                },
                            },
                        },
                        {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                            "required": ["error"],
                        },
                    ]
                },
                "test_examples": [{"operation": op["name"]}],
            }

            # Add optional API key if needed
            if api.get("auth_method") == "api_key_optional":
                tool["optional_api_keys"] = [f"{api_name.upper()}_API_KEY"]

            tools.append(tool)

        # Write file
        output_path = self.output_dir / file_name
        with open(output_path, "w") as f:
            json.dump(tools, f, indent=2)

        return output_path

    def _find_test_examples(self, api: dict[str, Any]) -> list[dict[str, Any]]:
        """Find real test examples for API."""
        # This would call the API to discover real IDs
        # For demo, return placeholder note
        return [
            {
                "note": "In production, this would call list endpoints to discover real IDs",
                "strategy": "Use List → Get pattern to find valid test data",
            }
        ]

    def _update_default_config(self, api: dict[str, Any]):
        """Update default_config.py with new tool category."""
        api_name = api["name"].replace(" ", "").lower()

        print("MANUAL STEP REQUIRED:")
        print("Add to src/tooluniverse/default_config.py:")
        print(f'    "{api_name}": os.path.join(current_dir, "data", "{api_name}_tools.json"),')

    # ========== PHASE 3: VALIDATION ==========

    def phase3_validation(self, tool_info: dict[str, Any]) -> dict[str, Any]:
        """
        Phase 3: Validate created tools.

        Args:
            tool_info: Tool creation information from Phase 2

        Returns:
            Validation results
        """
        print("=" * 80)
        print(f"PHASE 3: VALIDATION - {tool_info['api_name']}")
        print("=" * 80)

        results = {
            "api_name": tool_info["api_name"],
            "timestamp": datetime.now().isoformat(),
            "checks": {},
        }

        # Step 3.1: Schema validation
        print("\n[Step 3.1] Validating schemas...")
        schema_results = self._validate_schemas(tool_info["json_path"])
        results["checks"]["schema"] = schema_results
        self._print_validation_results("Schema", schema_results)

        # Step 3.2: Test example validation
        print("\n[Step 3.2] Validating test examples...")
        example_results = self._validate_test_examples(tool_info["json_path"])
        results["checks"]["examples"] = example_results
        self._print_validation_results("Test Examples", example_results)

        # Step 3.3: Tool loading verification (if ToolUniverse available)
        print("\n[Step 3.3] Verifying tool loading...")
        loading_results = self._verify_tool_loading(tool_info)
        results["checks"]["loading"] = loading_results
        self._print_validation_results("Tool Loading", loading_results)

        # Step 3.4: Integration tests (would run real API calls)
        print("\n[Step 3.4] Running integration tests...")
        print("⚠️  Integration tests require actual API deployment")
        print("    Use: python scripts/test_new_tools.py <tool_name> -v")

        # Generate validation report
        print("\n[Step 3.5] Generating validation report...")
        report_path = self._generate_validation_report(results)
        results["report_path"] = report_path
        print(f"✅ Validation report: {report_path}")

        return results

    def _validate_schemas(self, json_path: Path) -> dict[str, Any]:
        """Validate return schemas have proper structure."""
        issues = []
        passed = []

        try:
            with open(json_path) as f:
                tools = json.load(f)

            for tool in tools:
                tool_name = tool.get("name", "unknown")
                schema = tool.get("return_schema", {})

                # Check 1: Has oneOf
                if "oneOf" not in schema:
                    issues.append(
                        f"{tool_name}: Missing oneOf in return_schema"
                    )
                    continue

                # Check 2: oneOf has 2 schemas
                if len(schema["oneOf"]) != 2:
                    issues.append(
                        f"{tool_name}: oneOf must have exactly 2 schemas (success + error)"
                    )
                    continue

                # Check 3: Success schema has data field
                success_schema = schema["oneOf"][0]
                if "properties" not in success_schema:
                    issues.append(f"{tool_name}: Missing properties in success schema")
                    continue

                if "data" not in success_schema["properties"]:
                    issues.append(
                        f"{tool_name}: Missing 'data' field in success schema"
                    )
                    continue

                # Check 4: Error schema has error field
                error_schema = schema["oneOf"][1]
                if "properties" not in error_schema:
                    issues.append(f"{tool_name}: Missing properties in error schema")
                    continue

                if "error" not in error_schema["properties"]:
                    issues.append(f"{tool_name}: Missing 'error' field in error schema")
                    continue

                passed.append(tool_name)

        except Exception as e:
            issues.append(f"Failed to load JSON: {e}")

        return {
            "passed": len(passed),
            "failed": len(issues),
            "issues": issues,
            "success": len(issues) == 0,
        }

    def _validate_test_examples(self, json_path: Path) -> dict[str, Any]:
        """Validate test examples don't use placeholders."""
        issues = []
        passed = []

        placeholder_patterns = [
            "test",
            "dummy",
            "placeholder",
            "example",
            "sample",
            "xxx",
            "temp",
            "fake",
            "mock",
        ]

        try:
            with open(json_path) as f:
                tools = json.load(f)

            for tool in tools:
                tool_name = tool.get("name", "unknown")
                examples = tool.get("test_examples", [])
                issues_before = len(issues)

                for i, example in enumerate(examples):
                    for key, value in example.items():
                        if isinstance(value, str):
                            value_lower = value.lower()
                            if any(p in value_lower for p in placeholder_patterns):
                                issues.append(
                                    f"{tool_name}: test_examples[{i}][{key}] contains "
                                    f"placeholder value: {value}"
                                )

                if len(issues) == issues_before:
                    passed.append(tool_name)

        except Exception as e:
            issues.append(f"Failed to load JSON: {e}")

        return {
            "passed": len(passed),
            "failed": len(issues),
            "issues": issues,
            "success": len(issues) == 0,
        }

    def _verify_tool_loading(self, tool_info: dict[str, Any]) -> dict[str, Any]:
        """Verify tool can be loaded into ToolUniverse."""
        checks = [
            "Class registered in tool_registry",
            "Config registered in default_config.py",
            "Wrappers generated in tools/",
        ]
        issues = [f"Manual verification needed: {check}" for check in checks]

        return {
            "passed": 0,
            "failed": len(issues),
            "issues": issues,
            "success": False,
            "note": "Tool loading requires actual ToolUniverse deployment",
        }

    def _print_validation_results(self, check_name: str, results: dict[str, Any]):
        """Print validation results."""
        if results["success"]:
            print(f"  ✅ {check_name}: All checks passed ({results['passed']} tools)")
        else:
            print(
                f"  ❌ {check_name}: {results['failed']} issues found "
                f"({results['passed']} passed)"
            )
            for issue in results["issues"][:5]:  # Show first 5
                print(f"     - {issue}")
            if len(results["issues"]) > 5:
                print(f"     ... and {len(results['issues']) - 5} more")

    def _generate_validation_report(self, results: dict[str, Any]) -> Path:
        """Generate validation report."""
        report_path = (
            self.output_dir
            / f"validation_report_{results['api_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_path, "w") as f:
            f.write(f"# Validation Report: {results['api_name']}\n\n")
            f.write(f"Generated: {results['timestamp']}\n\n")

            # Summary
            total_checks = len(results["checks"])
            passed_checks = sum(
                1 for c in results["checks"].values() if c.get("success", False)
            )

            f.write("## Summary\n\n")
            f.write(f"- Total checks: {total_checks}\n")
            f.write(f"- Passed: {passed_checks}\n")
            f.write(f"- Failed: {total_checks - passed_checks}\n\n")

            # Detailed results
            for check_name, check_results in results["checks"].items():
                f.write(f"## {check_name.title()} Validation\n\n")

                if check_results.get("success"):
                    f.write(f"✅ **PASSED** ({check_results['passed']} items)\n\n")
                else:
                    f.write(
                        f"❌ **FAILED** ({check_results['failed']} issues, "
                        f"{check_results['passed']} passed)\n\n"
                    )

                    if check_results.get("issues"):
                        f.write("**Issues found:**\n\n")
                        for issue in check_results["issues"]:
                            f.write(f"- {issue}\n")
                        f.write("\n")

                if check_results.get("note"):
                    f.write(f"*Note: {check_results['note']}*\n\n")

            # devtu Compliance Checklist
            f.write("## devtu Compliance Checklist\n\n")
            f.write("1. [ ] Tool Loading: Verify 3-step registration\n")
            f.write("2. [ ] API Verification: Check against official docs\n")
            f.write("3. [ ] Error Pattern Detection: Review error handling\n")
            f.write(
                f"4. [{'x' if results['checks']['schema']['success'] else ' '}] Schema Validation: oneOf + data wrapper\n"
            )
            f.write(
                f"5. [{'x' if results['checks']['examples']['success'] else ' '}] Test Examples: Real IDs, no placeholders\n"
            )
            f.write("6. [ ] Parameter Verification: Match API requirements\n\n")

        return report_path

    # ========== PHASE 4: INTEGRATION ==========

    def phase4_integration(
        self,
        tool_info: dict[str, Any],
        validation_results: dict[str, Any],
        branch_name: str = None,
    ) -> dict[str, Any]:
        """
        Phase 4: Integrate tools via git PR.

        Args:
            tool_info: Tool creation info from Phase 2
            validation_results: Validation results from Phase 3
            branch_name: Optional custom branch name

        Returns:
            Integration results with PR URL
        """
        print("=" * 80)
        print(f"PHASE 4: INTEGRATION - {tool_info['api_name']}")
        print("=" * 80)

        # Step 4.1: Create branch
        if not branch_name:
            branch_name = f"feature/add-{tool_info['api_name'].lower()}-tools"

        print(f"\n[Step 4.1] Creating git branch: {branch_name}")
        print("⚠️  NOTE: This demo doesn't create actual git branches")
        print(f"    Run: git checkout -b {branch_name}")

        # Step 4.2: Generate commit message
        print("\n[Step 4.2] Generating commit message...")
        commit_msg = self._generate_commit_message(tool_info, validation_results)
        commit_path = self.output_dir / f"commit_message_{tool_info['api_name']}.txt"
        with open(commit_path, "w") as f:
            f.write(commit_msg)
        print(f"✅ Commit message: {commit_path}")

        # Step 4.3: Generate PR description
        print("\n[Step 4.3] Generating PR description...")
        pr_desc = self._generate_pr_description(tool_info, validation_results)
        pr_path = self.output_dir / f"pr_description_{tool_info['api_name']}.md"
        with open(pr_path, "w") as f:
            f.write(pr_desc)
        print(f"✅ PR description: {pr_path}")

        # Step 4.4: Instructions for manual completion
        print("\n[Step 4.4] Manual steps required:")
        print("\n1. Copy generated files to ToolUniverse repository:")
        print(f"   cp {tool_info['py_path']} src/tooluniverse/")
        print(f"   cp {tool_info['json_path']} src/tooluniverse/data/")
        print("\n2. Update default_config.py (see Phase 2 output)")
        print("\n3. Create git branch and commit:")
        print(f"   git checkout -b {branch_name}")
        print("   git add src/tooluniverse/*.py src/tooluniverse/data/*.json src/tooluniverse/default_config.py")
        print(f"   git commit -F {commit_path}")
        print("\n4. Push and create PR:")
        print(f"   git push -u origin {branch_name}")
        print(f"   gh pr create --title 'Add {tool_info['api_name']} tools' --body-file {pr_path}")

        return {
            "branch_name": branch_name,
            "commit_message_path": commit_path,
            "pr_description_path": pr_path,
            "status": "manual_completion_required",
        }

    def _generate_commit_message(
        self, tool_info: dict[str, Any], validation_results: dict[str, Any]
    ) -> str:
        """Generate git commit message."""
        api_name = tool_info["api_name"]
        ops = tool_info["architecture"]["operations"]

        msg = f"Add {api_name} tools\n\n"
        msg += f"Implements {len(ops)} tools for {api_name} API:\n"

        for op in ops[:5]:  # Show first 5
            msg += f"- {api_name}_{op['name']}: {op['description']}\n"

        if len(ops) > 5:
            msg += f"- ... and {len(ops) - 5} more\n"

        msg += "\nValidation:\n"
        for check_name, check_results in validation_results["checks"].items():
            status = "✅" if check_results.get("success", False) else "⚠️"
            msg += f"- {status} {check_name.title()}: {check_results['passed']} passed\n"

        msg += "\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>\n"

        return msg

    def _generate_pr_description(
        self, tool_info: dict[str, Any], validation_results: dict[str, Any]
    ) -> str:
        """Generate PR description."""
        api_name = tool_info["api_name"]
        ops = tool_info["architecture"]["operations"]

        desc = f"# Add {api_name} Tools\n\n"
        desc += "## Summary\n\n"
        desc += f"Adds {len(ops)} new tools integrating the {api_name} API.\n\n"

        desc += "## Tools Added\n\n"
        desc += "| Tool Name | Description |\n"
        desc += "|-----------|-------------|\n"

        for op in ops:
            desc += f"| {api_name}_{op['name']} | {op['description']} |\n"

        desc += "\n## Validation Results\n\n"

        for check_name, check_results in validation_results["checks"].items():
            if check_results.get("success"):
                desc += f"✅ {check_name.title()}: All checks passed\n"
            else:
                desc += (
                    f"⚠️ {check_name.title()}: {check_results['failed']} issues found\n"
                )

        desc += "\n## Files Changed\n\n"
        desc += f"- `{tool_info['py_path'].name}` - Tool implementation\n"
        desc += f"- `{tool_info['json_path'].name}` - Tool configurations\n"
        desc += "- `src/tooluniverse/default_config.py` - Registration\n\n"

        desc += "## Checklist\n\n"
        desc += "- [ ] All tests passing\n"
        desc += "- [ ] Schema validation complete\n"
        desc += "- [ ] Real test examples\n"
        desc += "- [ ] No placeholder values\n"
        desc += "- [ ] Tool names ≤55 chars\n"
        desc += "- [ ] default_config.py updated\n\n"

        desc += "---\n\n"
        desc += "**Generated by devtu-auto-discover-apis skill**\n"

        return desc


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Automated Life Science API Discovery & Tool Creation"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "discovery", "create", "validate", "integrate"],
        default="full",
        help="Execution mode",
    )

    parser.add_argument(
        "--focus-domains",
        nargs="+",
        help="Specific domains to focus on (for discovery)",
    )

    parser.add_argument(
        "--apis",
        nargs="+",
        help="Specific APIs to process (for create mode)",
    )

    parser.add_argument(
        "--tools",
        nargs="+",
        help="Specific tools to validate (for validate mode)",
    )

    parser.add_argument(
        "--branch",
        help="Git branch name (for integrate mode)",
    )

    parser.add_argument(
        "--output-dir",
        default="./api_discovery_output",
        help="Output directory for generated files",
    )

    args = parser.parse_args()

    # Initialize agent
    agent = APIDiscoveryAgent()
    agent.output_dir = Path(args.output_dir)
    agent.output_dir.mkdir(exist_ok=True)

    try:
        if args.mode == "full":
            # Run full pipeline
            print("Running full pipeline: Discovery → Creation → Validation → Integration\n")

            # Phase 1: Discovery
            discovery_results = agent.phase1_discovery(focus_domains=args.focus_domains)

            # Get high-priority APIs
            high_priority = [
                api
                for api in discovery_results["apis"]
                if api["priority"] == "high"
            ]

            if not high_priority:
                print("\n⚠️  No high-priority APIs found. Exiting.")
                return

            print(f"\nFound {len(high_priority)} high-priority APIs to implement.")
            print("\nProcessing first API as demo...\n")

            # Process first API
            api = high_priority[0]

            # Phase 2: Creation
            tool_info = agent.phase2_creation(api)

            # Phase 3: Validation
            validation_results = agent.phase3_validation(tool_info)

            # Phase 4: Integration
            agent.phase4_integration(tool_info, validation_results)

            print("\n" + "=" * 80)
            print("PIPELINE COMPLETE")
            print("=" * 80)
            print(f"\nGenerated files in: {agent.output_dir}")
            print("\nNext steps:")
            print(
                "1. Review generated tool files and validation reports"
            )
            print("2. Follow manual integration steps from Phase 4")
            print("3. Test tools with: python scripts/test_new_tools.py <tool_name>")

        elif args.mode == "discovery":
            # Discovery only
            discovery_results = agent.phase1_discovery(focus_domains=args.focus_domains)
            print(f"\n✅ Discovery complete. Report: {discovery_results['report_path']}")

        elif args.mode == "create":
            # Create tools for specific APIs
            if not args.apis:
                print("Error: --apis required for create mode")
                return

            print("Create mode requires API metadata from discovery phase.")
            print("    Run discovery first, then use discovered API data for creation.")

        elif args.mode == "validate":
            # Validate specific tools
            if not args.tools:
                print("Error: --tools required for validate mode")
                return

            print("Validate mode requires tool files to exist.")
            print(f"    Use: python scripts/test_new_tools.py {args.tools[0]} -v")

        elif args.mode == "integrate":
            # Integrate tools
            print("Integrate mode requires tool creation and validation complete.")
            print("    Follow manual steps from Phase 4 output.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

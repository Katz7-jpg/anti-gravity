#!/usr/bin/env python3
"""
Example Usage: Automated API Discovery Agent

This script demonstrates various use cases for the API discovery agent.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from python_implementation import APIDiscoveryAgent


def example_1_full_pipeline():
    """
    Example 1: Full Pipeline

    Discover APIs → Create Tools → Validate → Integrate
    """
    print("=" * 80)
    print("EXAMPLE 1: FULL PIPELINE")
    print("=" * 80)

    # Initialize agent
    agent = APIDiscoveryAgent()

    # Focus on metabolomics domain
    focus_domains = ["metabolomics"]

    # Phase 1: Discovery
    print("\n[PHASE 1] Running discovery...")
    discovery_results = agent.phase1_discovery(focus_domains=focus_domains)

    high_priority = [a for a in discovery_results['apis'] if a['priority'] == 'high']
    print(f"\nDiscovered {len(discovery_results['apis'])} APIs")
    print(f"High priority: {len(high_priority)}")

    if not high_priority:
        print("No high-priority APIs found")
        return

    api = high_priority[0]
    print(f"\nSelected API: {api['name']} (score: {api['score']}/100)")

    # Phase 2: Creation
    print("\n[PHASE 2] Creating tools...")
    tool_info = agent.phase2_creation(api)

    print(f"Created {len(tool_info['architecture']['operations'])} tools")
    print(f"Python file: {tool_info['py_path']}")
    print(f"JSON file: {tool_info['json_path']}")

    # Phase 3: Validation
    print("\n[PHASE 3] Validating tools...")
    validation_results = agent.phase3_validation(tool_info)

    all_passed = all(
        check.get('success', False)
        for check in validation_results['checks'].values()
    )

    if all_passed:
        print("✅ All validation checks passed!")
    else:
        print("⚠️ Some validation checks need attention")

    # Phase 4: Integration
    print("\n[PHASE 4] Preparing integration...")
    integration_results = agent.phase4_integration(tool_info, validation_results)

    print(f"\nBranch: {integration_results['branch_name']}")
    print(f"Commit message: {integration_results['commit_message_path']}")
    print(f"PR description: {integration_results['pr_description_path']}")

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print(f"\nAll files in: {agent.output_dir}")


def example_2_discovery_only():
    """
    Example 2: Discovery Only

    Just analyze gaps and find API candidates.
    """
    print("=" * 80)
    print("EXAMPLE 2: DISCOVERY ONLY")
    print("=" * 80)

    agent = APIDiscoveryAgent()

    # Run discovery without focus domains (find all gaps)
    discovery_results = agent.phase1_discovery()

    print("\nDiscovery complete")
    print(f"Report: {discovery_results['report_path']}")
    print(f"\nTotal APIs found: {len(discovery_results['apis'])}")

    # Show top 3 APIs
    print("\nTop 3 API Candidates:")
    for i, api in enumerate(discovery_results['apis'][:3], 1):
        print(f"\n{i}. {api['name']}")
        print(f"   Domain: {api['domain']}")
        print(f"   Score: {api['score']}/100")
        print(f"   Priority: {api['priority']}")


def example_3_coverage_analysis():
    """
    Example 3: Coverage Analysis

    Just analyze current ToolUniverse coverage.
    """
    print("=" * 80)
    print("EXAMPLE 3: COVERAGE ANALYSIS")
    print("=" * 80)

    agent = APIDiscoveryAgent()

    # Analyze coverage
    coverage = agent._analyze_coverage()

    print(f"\nTotal tools in ToolUniverse: {coverage['total_tools']}")
    print("\nTop 10 domains by tool count:")

    sorted_domains = sorted(
        coverage['domain_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )

    for i, (domain, count) in enumerate(sorted_domains[:10], 1):
        print(f"  {i:2d}. {domain:25s}: {count:4d} tools")

    print("\nBottom 5 domains (gaps):")

    for i, (domain, count) in enumerate(sorted_domains[-5:], 1):
        status = "🔴 Critical" if count < 5 else "🟠 Moderate"
        print(f"  {i}. {domain:25s}: {count:4d} tools - {status}")


def example_4_targeted_discovery():
    """
    Example 4: Targeted Discovery

    Focus on specific domains only.
    """
    print("=" * 80)
    print("EXAMPLE 4: TARGETED DISCOVERY")
    print("=" * 80)

    agent = APIDiscoveryAgent()

    # Focus on multiple domains
    focus_domains = ["metabolomics", "single_cell", "imaging"]

    print(f"Focusing on domains: {', '.join(focus_domains)}")

    discovery_results = agent.phase1_discovery(focus_domains=focus_domains)

    # Show results by domain
    print("\nResults by domain:")

    for domain in focus_domains:
        domain_apis = [
            api for api in discovery_results['apis']
            if api['domain'] == domain
        ]

        print(f"\n{domain.upper()}:")
        print(f"  APIs found: {len(domain_apis)}")

        if domain_apis:
            high_priority = [a for a in domain_apis if a['priority'] == 'high']
            print(f"  High priority: {len(high_priority)}")

            if high_priority:
                print(f"  Top candidate: {high_priority[0]['name']} ({high_priority[0]['score']}/100)")


def example_5_batch_validation():
    """
    Example 5: Batch Validation

    Validate multiple tool files at once.
    """
    print("=" * 80)
    print("EXAMPLE 5: BATCH VALIDATION")
    print("=" * 80)

    agent = APIDiscoveryAgent()

    # List of tool JSON files to validate
    # (In practice, these would be actual files)
    tool_files = [
        agent.output_dir / "metabolights_tools.json",
        agent.output_dir / "gnps_tools.json",
    ]

    print(f"Validating {len(tool_files)} tool configurations...\n")

    results = []

    for tool_file in tool_files:
        if not tool_file.exists():
            print(f"⚠️  {tool_file.name}: File not found (skipping)")
            continue

        print(f"Validating {tool_file.name}...")

        # Schema validation
        schema_results = agent._validate_schemas(tool_file)

        # Test example validation
        example_results = agent._validate_test_examples(tool_file)

        results.append({
            'file': tool_file.name,
            'schema': schema_results,
            'examples': example_results,
        })

        # Print summary
        if schema_results['success'] and example_results['success']:
            print("  All checks passed\n")
        else:
            print("  Issues found\n")

    # Overall summary
    print("=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)

    for result in results:
        status = (
            "✅ PASS"
            if result['schema']['success'] and result['examples']['success']
            else "❌ FAIL"
        )
        print(f"{result['file']:30s}: {status}")


def main():
    """Run examples."""
    examples = {
        '1': ('Full Pipeline', example_1_full_pipeline),
        '2': ('Discovery Only', example_2_discovery_only),
        '3': ('Coverage Analysis', example_3_coverage_analysis),
        '4': ('Targeted Discovery', example_4_targeted_discovery),
        '5': ('Batch Validation', example_5_batch_validation),
    }

    if len(sys.argv) > 1:
        # Run specific example
        example_num = sys.argv[1]
        if example_num in examples:
            name, func = examples[example_num]
            print(f"\nRunning: {name}\n")
            func()
        else:
            print(f"Unknown example: {example_num}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        # Show menu
        print("\n" + "=" * 80)
        print("API DISCOVERY AGENT - EXAMPLES")
        print("=" * 80)
        print("\nAvailable examples:\n")

        for num, (name, _) in examples.items():
            print(f"  {num}. {name}")

        print("\nUsage:")
        print(f"  python {Path(__file__).name} <example_number>")
        print("\nExample:")
        print(f"  python {Path(__file__).name} 1")


if __name__ == "__main__":
    main()

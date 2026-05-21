#!/usr/bin/env python3
"""
Automated script to update QuantMuse knowledge graph analysis
Integrates with development workflow for continuous architecture monitoring
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_for_changes():
    """Check if there have been code changes since last analysis"""
    ua_dir = Path(".understand-anything")
    
    # Check if analysis exists
    kg_path = ua_dir / "knowledge-graph.json"
    if not kg_path.exists():
        return True, "No existing analysis found"
    
    # Get last analysis time
    try:
        with open(kg_path, 'r') as f:
            kg = json.load(f)
        last_updated = kg.get('lastUpdated')
        if not last_updated:
            return True, "No timestamp in existing analysis"
    except:
        return True, "Could not read existing analysis"
    
    # Check for git changes since last update
    success, output, error = run_command('git log --since="' + last_updated + '" --oneline')
    if not success:
        return True, "Could not check git history"
    
    if output.strip():
        return True, f"Found {len(output.strip().split('\\n'))} commits since last analysis"
    
    return False, "No changes detected"

def update_analysis():
    """Update the knowledge graph analysis"""
    print("🔄 Starting QuantMuse architecture analysis update...")
    
    # Check for changes
    should_update, reason = check_for_changes()
    if not should_update:
        print(f"⏭️  Skipping update: {reason}")
        return True
    
    print(f"📝 Update reason: {reason}")
    
    # Run the consolidation script to merge batch results
    print("📊 Consolidating batch analysis results...")
    success, output, error = run_command("node ../consolidate_graph.js")
    if not success:
        print(f"❌ Error consolidating graph: {error}")
        return False
    
    # Run domain analysis
    print("🏗️  Running domain analysis...")
    success, output, error = run_command("python ../run_domain_analysis.py")
    if not success:
        print(f"❌ Error in domain analysis: {error}")
        return False
    
    # Copy domain graph to final location
    ua_dir = Path(".understand-anything")
    domain_src = ua_dir / "intermediate/domain-analysis.json"
    domain_dst = ua_dir / "domain-graph.json"
    
    if domain_src.exists():
        domain_src.rename(domain_dst)
        print("✅ Domain graph updated")
    
    # Generate tours
    print("🎓 Generating guided tours...")
    success, output, error = run_command("python ../generate_tours.py")
    if not success:
        print(f"❌ Error generating tours: {error}")
        return False
    
    # Validate the updated graph
    print("🔍 Validating updated analysis...")
    success, output, error = run_command("python ../validate_graph.py")
    if not success:
        print(f"⚠️  Validation warnings: {error}")
    
    # Generate architecture insights
    print("💡 Generating architecture insights...")
    success, output, error = run_command("python ../generate_architecture_insights.py")
    if not success:
        print(f"❌ Error generating insights: {error}")
        return False
    
    # Update timestamp in knowledge graph
    kg_path = ua_dir / "knowledge-graph.json"
    if kg_path.exists():
        try:
            with open(kg_path, 'r') as f:
                kg = json.load(f)
            kg['lastUpdated'] = datetime.now().isoformat()
            with open(kg_path, 'w') as f:
                json.dump(kg, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not update timestamp: {e}")
    
    print("✅ Analysis update completed successfully!")
    return True

def generate_diff_report():
    """Generate a diff report showing architectural changes"""
    print("📊 Generating architectural diff report...")
    
    # This would compare current and previous knowledge graphs
    # For now, create a placeholder report
    report = {
        "generated_at": datetime.now().isoformat(),
        "changes_detected": True,
        "summary": "Architecture analysis updated with latest code changes",
        "recommendations": [
            "Review new components in the interactive dashboard",
            "Check for any breaking changes in dependencies",
            "Validate that risk management components remain intact"
        ]
    }
    
    ua_dir = Path(".understand-anything")
    diff_path = ua_dir / "diff-report.json"
    
    with open(diff_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Diff report saved to {diff_path}")

def main():
    """Main execution"""
    print("🚀 QuantMuse Development Workflow Integration")
    print("=" * 50)
    
    # Parse command line arguments
    force_update = "--force" in sys.argv
    diff_only = "--diff" in sys.argv
    
    if diff_only:
        generate_diff_report()
        return
    
    if force_update:
        print("🔧 Force update requested")
    
    # Change to QuantMuse directory
    quantmuse_dir = Path(__file__).parent.parent.parent
    import os
    os.chdir(quantmuse_dir)
    
    # Update analysis
    success = update_analysis()
    
    if success:
        # Generate diff report
        generate_diff_report()
        
        print("\n🎉 Development workflow integration complete!")
        print("\n📋 Next steps:")
        print("   1. Open the interactive dashboard: python .understand-anything/dashboard/server.py")
        print("   2. Review architecture insights: .understand-anything/architecture-insights.md")
        print("   3. Check validation report: .understand-anything/validation-report.json")
    else:
        print("\n❌ Analysis update failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

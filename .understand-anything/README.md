# QuantMuse Knowledge Graph Analysis

This directory contains the complete Understand-Anything analysis of the QuantMuse quantitative trading system, providing interactive visualization and comprehensive insights into the system architecture.

## 📊 Analysis Components

### 🏗️ Knowledge Graph
- **`knowledge-graph.json`** - Complete structural analysis of all components, classes, and dependencies
- **`domain-graph.json`** - Business domain analysis showing trading flows and processes
- **`tours.json`** - Guided learning tours for understanding the architecture

### 📈 Interactive Dashboard
- **`dashboard/index.html`** - Web-based interactive visualization
- **`dashboard/server.py`** - Local server for dashboard access

### 📋 Analysis Reports
- **`architecture-insights.json`** - Detailed architectural analysis and recommendations
- **`architecture-insights.md`** - Human-readable insights report
- **`validation-report.json`** - Graph completeness and validation results

### 🔧 Development Tools
- **`scripts/update_analysis.py`** - Automated analysis updates
- **`scripts/dev_tools.py`** - Developer utilities for exploring the architecture

## 🚀 Quick Start

### 1. Open Interactive Dashboard
```bash
# Option 1: Open static dashboard in browser
python .understand-anything/scripts/dev_tools.py dashboard

# Option 2: Start local server
python .understand-anything/dashboard/server.py
# Then visit http://localhost:8080
```

### 2. Explore Architecture
```bash
# Get architecture overview
python .understand-anything/scripts/dev_tools.py overview

# Search for components
python .understand-anything/scripts/dev_tools.py search --query "risk"

# View component details
python .understand-anything/scripts/dev_tools.py details --id "file:backend/include/risk_manager.hpp"

# List guided tours
python .understand-anything/scripts/dev_tools.py tours

# Find critical components
python .understand-anything/scripts/dev_tools.py critical
```

### 3. Update Analysis
```bash
# Update with latest code changes
python .understand-anything/scripts/update_analysis.py

# Force complete rebuild
python .understand-anything/scripts/update_analysis.py --force

# Generate diff report only
python .understand-anything/scripts/update_analysis.py --diff
```

## 📊 Dashboard Features

### Structural View
- **Interactive Graph**: Explore all 65+ system components
- **Filtering**: Filter by node type, complexity, and tags
- **Node Details**: Click components to see summaries and relationships
- **Color Coding**: Visual distinction between file types, classes, and configurations

### Domain View
- **Business Flows**: 4 end-to-end trading processes
- **Process Steps**: 10 detailed implementation steps
- **Domain Relationships**: Cross-domain dependencies and interactions

### Guided Tours
- **Architecture Overview** (15 min, beginner)
- **Data Flow Pipeline** (12 min, intermediate)
- **Trading Strategy Framework** (10 min, advanced)
- **AI/ML Integration** (8 min, advanced)

## 🏗️ Architecture Insights

### Key Findings
- **Hybrid Architecture**: Python for data processing/AI, C++ for performance-critical trading
- **65 Components**: Organized into 5 major business domains
- **Multi-Source Data**: Integration with Binance, Yahoo Finance, Alpha Vantage
- **AI/ML Integration**: Sentiment analysis, LLM-powered market insights

### Business Domains
1. **Trading Data Management** - Market data acquisition and processing
2. **Quantitative Analysis** - Factor analysis and stock screening
3. **AI/ML Integration** - Sentiment analysis and prediction models
4. **Trading Strategy Execution** - Order execution with risk management
5. **Backtesting & Analysis** - Strategy validation and performance analysis

### Critical Components
- Risk Management System
- Order Execution Engine
- Factor Analysis Pipeline
- AI/ML Integration Layer
- Real-time Data Processing

## 🔍 Development Workflow Integration

### Automated Updates
The analysis can be automatically updated when code changes:
```bash
# Add to git hooks or CI/CD pipeline
python .understand-anything/scripts/update_analysis.py
```

### Code Review Integration
- **Diff Analysis**: See architectural impact of changes
- **Dependency Validation**: Ensure changes don't break critical paths
- **Risk Assessment**: Identify changes affecting risk management components

### Onboarding New Developers
1. Start with the **Architecture Overview** tour
2. Explore the **Domain View** to understand business flows
3. Use **Search Tools** to find specific components
4. Review **Architecture Insights** for key recommendations

## 📋 File Structure

```
.understand-anything/
├── knowledge-graph.json          # Complete structural analysis
├── domain-graph.json             # Business domain analysis
├── tours.json                    # Guided learning tours
├── architecture-insights.md      # Human-readable insights
├── architecture-insights.json    # Detailed analysis data
├── validation-report.json        # Graph validation results
├── diff-report.json             # Change analysis report
├── dashboard/
│   ├── index.html               # Interactive web dashboard
│   └── server.py                # Local server script
├── scripts/
│   ├── update_analysis.py       # Automated updates
│   └── dev_tools.py             # Developer utilities
├── intermediate/                # Temporary analysis files
└── tmp/                         # Scratch files
```

## 🛠️ Advanced Usage

### Custom Analysis
```python
from .understand-anything.scripts.dev_tools import QuantMuseDevTools

tools = QuantMuseDevTools()

# Search for specific patterns
risk_components = tools.search_components("risk", node_type="class")

# Get component relationships
details = tools.get_component_details("file:backend/include/risk_manager.hpp")

# Find critical components
critical = tools.get_critical_components()
```

### Integration with IDE
The knowledge graph can be integrated with IDEs for:
- **Code Navigation**: Jump between related components
- **Context Awareness**: Understand component relationships while coding
- **Documentation**: Auto-generate component documentation

## 📞 Support

For questions about the analysis or tools:
1. Check the **Architecture Insights** report
2. Use the **Interactive Dashboard** for exploration
3. Run `python .understand-anything/scripts/dev_tools.py --help` for tool usage

## 🔄 Maintenance

### Regular Updates
- Run `update_analysis.py` after major code changes
- Review `validation-report.json` for any issues
- Check `architecture-insights.md` for new recommendations

### Performance
- Large graphs (>1000 nodes) may need filtering
- Use node type filters for focused exploration
- Consider git-lfs for large knowledge graphs in version control

---

*Generated by Understand-Anything on 2026-05-11*

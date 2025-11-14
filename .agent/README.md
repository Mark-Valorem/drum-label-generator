# .agent Documentation Index

**version:** v1.0.0
**Last Updated:** 2025-11-14
**Project:** Drum Label Generator for Valorem Chemicals

## Purpose

This file serves as the master index for all AI agent documentation. Read this first before implementing any features to understand available context.

## Quick Start

1. For new features: Review relevant **System** docs and **Tasks** for similar implementations
2. For specific processes: Check **SOPs** for step-by-step guides
3. When stuck: Search this index for related documentation

---

## Project Status

**Stage:** Production (v1.0.0)
**Total Documents:** 2 system docs, 2 SOPs, 0 tasks
**Last Feature:** Initial .agent documentation system setup

---

## System Documentation

Core system documentation describing the project architecture and components.

### Available System Docs:

#### [architecture.md](.agent/system/architecture.md)
- Project file structure and organization
- Main components: DrumLabelGenerator class, config system
- Data flow: CSV/Excel → Python processing → PDF output
- Dependencies and their roles

#### [label-layout.md](.agent/system/label-layout.md)
- A5 label design specifications
- Section breakdown (header, table, pictograms, barcodes, QR codes)
- Measurements and positioning logic
- Configuration options in config.py

---

## Standard Operating Procedures (SOPs)

Step-by-step guides for common development and operational tasks.

### Available SOPs:

#### [git-workflow.md](.agent/sops/git-workflow.md)
- Branching strategy and commit conventions
- Conventional commits format (feat, fix, docs, refactor, test, chore)
- Pull request process
- Version tagging guidelines

#### [project-setup.md](.agent/sops/project-setup.md)
- Development environment setup
- Installing Python dependencies
- Downloading GHS pictogram assets
- Running test suite
- First label generation

### Planned SOPs:

- `adding-feature.md` - Process for adding new label sections or data fields
- `testing-labels.md` - Quality assurance checklist for label output
- `troubleshooting.md` - Common issues and solutions
- `data-integration.md` - Integrating with Unleashed or other ERP systems

---

## Implementation Tasks

This section will populate as features are implemented and documented.

### Planned Task Documentation:

- Initial project setup and .agent system implementation
- Future feature additions (API integration, web interface, multi-label layouts)

---

## Documentation Maintenance

### When to Update

- **After completing any feature** → Run `/update-doc` to save implementation plan
- **After correcting agent mistakes** → Run `/update-doc generate SOP for [process]`
- **After architectural changes** → Update `system/architecture.md`
- **When data format changes** → Update `system/label-layout.md` and related docs
- **When patterns emerge** → Create relevant SOPs

### How to Update

```bash
# After implementing features
/update-doc

# To create specific SOP
/update-doc generate SOP for [process name]

# For major refactors
/update-doc major
```

### Versioning

- Documentation follows semantic versioning
- Current version: v1.0.0
- Version increments automatically on updates
- Patch (v1.0.x): Minor updates, new SOPs, corrections
- Minor (v1.x.0): New major features, significant SOPs
- Major (v2.0.0): Complete restructure, breaking changes

---

## Context Management Tips

### For Large Features

1. Use sub-agents for research phase to isolate context
2. Reference this README at start of implementation
3. Run `/compact` after completing discrete tasks
4. Break large features into smaller, documented tasks

### For Troubleshooting

1. Check relevant SOPs first
2. Review implementation tasks for similar features
3. Verify against system documentation
4. Document solution as SOP if it's a common issue

### For Optimal Performance

- **Before planning:** Read this README first
- **During development:** Reference relevant SOPs and system docs
- **After implementation:** Update documentation immediately
- **Regular maintenance:** Review and archive outdated docs quarterly

---

## Git Automation

All documentation updates automatically:
1. Increment version numbers
2. Move unused files to `archive/`
3. Commit with descriptive message
4. Push to GitHub remote

---

## Project-Specific Context

**Business Domain:** Chemical manufacturing and labelling
**Compliance Focus:** Australian WHS regulations, GHS Revision 7, ADG Code
**Primary User:** Valorem Chemicals operations team
**Integration Points:** Unleashed ERP (CSV/Excel exports)
**Output:** Print-ready PDF labels for industrial drum labelling

**Key Terminology:**
- **GHS**: Globally Harmonized System for hazard classification
- **UN Number**: United Nations dangerous goods identifier
- **Batch Number**: Manufacturing lot identifier for traceability
- **ADG Code**: Australian Dangerous Goods Code
- **Proper Shipping Name**: Official dangerous goods transport designation

---

*This index will grow as the project develops. Keep it updated and organized.*

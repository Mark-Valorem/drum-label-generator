# Task: Initialize .agent Documentation System for New Project

## Objective
Set up a comprehensive AI-optimized documentation system from the start of this new project. This will establish the .agent folder structure, create configuration files, generate initial documentation templates, and configure Git automation to ensure consistent, efficient AI-assisted development from day one.

## Phase 1: Project Discovery & Planning

### 1.1 Gather Project Information
Ask the user about:
- **Project Name**: What is this project called?
- **Project Type**: Web app, API, mobile app, library, CLI tool, etc.?
- **Tech Stack**: Languages, frameworks, databases you plan to use
- **Development Team Size**: Solo or team? How many developers?
- **Primary Goals**: What will this project do? (2-3 sentences)
- **Git Remote**: GitHub repository URL (if already created)

### 1.2 Confirm Tech Stack Details
Based on responses, confirm:
- Runtime environment (Node.js, Python, Ruby, Go, etc.)
- Framework (Express, Django, Next.js, FastAPI, Rails, etc.)
- Database (PostgreSQL, MongoDB, MySQL, SQLite, none, etc.)
- Testing framework preference (Jest, Pytest, RSpec, etc.)
- Package manager (npm, yarn, pnpm, pip, bundler, etc.)

## Phase 2: Create Project Structure

### 2.1 Initialize Git Repository (if not already done)
```bash
git init
git branch -M main
```

If GitHub remote URL provided:
```bash
git remote add origin [URL]
```

### 2.2 Create .agent Documentation Structure
```
.agent/
├── README.md
├── tasks/
├── system/
│   └── .gitkeep
└── sops/
    └── .gitkeep

.claude/
└── commands/
    └── update-doc.md

archive/
└── .gitkeep
```

### 2.3 Create Essential Configuration Files
- `.gitignore` (if doesn't exist, create with appropriate templates)
- `CLAUDE.md` in project root
- `.agent/README.md`
- `.claude/commands/update-doc.md`

## Phase 3: Generate Initial Documentation

### 3.1 Create CLAUDE.md
```markdown
# [Project Name] - AI Agent Documentation

**version:** v1.0.0  
**Last Updated:** [Current Date]

## Project Overview
[Brief description based on user input]

**Tech Stack:**
- Runtime: [e.g., Node.js 20.x]
- Framework: [e.g., Express 4.x]
- Database: [e.g., PostgreSQL 15.x]
- Testing: [e.g., Jest]

## Documentation Structure
This project uses a .agent folder for maintaining AI agent context:
- `.agent/tasks/` - Implementation plans and PRDs for completed features
- `.agent/system/` - Architecture, database schemas, API documentation
- `.agent/sops/` - Standard operating procedures for common tasks
- `.agent/README.md` - Master index of all documentation
- `archive/` - Archived/deprecated files

## Rules for AI Agent
1. **Before Implementation**: Always read `.agent/README.md` first to understand available context
2. **After Implementation**: Run `/update-doc` to document the work and update SOPs
3. **On Mistakes**: When corrected, generate SOP to prevent recurrence
4. **Research Tasks**: Use sub-agents for research-heavy features to isolate context
5. **After Discrete Tasks**: Run `/compact` to clean conversation history
6. **Version Control**: All documentation updates automatically commit and push to GitHub

## Code Style Guidelines
[Will be populated as patterns emerge - update as project grows]
- Use consistent naming conventions
- Write descriptive commit messages following conventional commits
- Document complex logic with inline comments
- Keep functions small and focused

## Testing Requirements
- Write tests for all new features
- Maintain minimum [X]% code coverage
- Run tests before committing
- Test edge cases and error conditions

## Common Commands
[Will be populated based on package.json/setup scripts]
- `[start-command]` - Start development server
- `[test-command]` - Run test suite
- `[build-command]` - Build for production
- `[lint-command]` - Run linter

## Project-Specific Conventions
[Will be established as project develops]

---

*This file should remain concise. Detailed information belongs in .agent/ documentation.*
```

### 3.2 Create update-doc.md Command
```markdown
# Update Documentation Command

**version:** v1.0.0

## Purpose
Automate creation and maintenance of the .agent documentation system with version control.

## Commands

### Update After Feature Implementation
\`\`\`
/update-doc
\`\`\`
**Actions:**
1. Review recent conversation for completed work
2. If implementation plan exists, save to \`tasks/[feature-name].md\`
3. Identify repeatable processes, create/update SOPs in \`sops/\`
4. Update \`README.md\` and increment patch version (v1.0.0 → v1.0.1)
5. Move any unused/deprecated files to \`archive/\` preserving folder structure
6. Commit and push changes to GitHub:
   \`\`\`bash
   git add .
   git commit -m "docs: update documentation system to v\${version}"
   git push origin main
   \`\`\`
7. Provide summary of all updates made

### Generate Specific SOP
\`\`\`
/update-doc generate SOP for [process name]
\`\`\`
**Actions:**
1. Create SOP document in \`sops/[process-name].md\`
2. Include standard SOP structure (see below)
3. Update \`README.md\` index and increment version
4. Move any deprecated docs to \`archive/\` with timestamp
5. Commit and push to GitHub with descriptive message
6. Confirm SOP created and indexed

### Major Documentation Refactor
\`\`\`
/update-doc major
\`\`\`
**Actions:**
1. Increment major version (v1.0.0 → v2.0.0)
2. Review all documentation for accuracy
3. Archive outdated content
4. Restructure if needed
5. Commit with "docs(major): " prefix

## SOP Document Structure
\`\`\`markdown
# SOP: [Process Name]

**version:** v1.0.0  
**Created:** [Date]  
**Last Updated:** [Date]

## When to Use
[Describe scenarios when this SOP applies]

## Prerequisites
[List required knowledge, tools, or setup]

## Process
1. [Step one with details]
2. [Step two with details]
3. [Continue with numbered steps...]

## Related Documentation
- [Reference to system docs]
- [Reference to other SOPs]

## Common Mistakes
- **Mistake:** [Description]
  - **Solution:** [How to avoid/fix]

## Example
[Concrete example if helpful]
\`\`\`

## Versioning Rules
- **Patch (v1.0.0 → v1.0.1)**: Minor updates, new SOPs, small corrections
- **Minor (v1.0.0 → v1.1.0)**: New major features documented, significant SOPs added
- **Major (v1.0.0 → v2.0.0)**: Complete documentation restructure, breaking changes

## Archiving Rules
When moving files to \`archive/\`:
1. Preserve original folder structure: \`archive/[date]/[original-path]\`
2. Add README.md in archive folder explaining why files were archived
3. Update main README.md to remove references to archived content

## Rules for Creating Documentation
- Keep documentation **concise** and **action-oriented**
- Use **markdown** formatting for readability
- Include **specific file paths** and **command examples**
- Cross-reference related documentation
- Update README.md whenever new docs are added
- Always increment version numbers
- Commit and push after every documentation change
```

### 3.3 Create .agent/README.md
```markdown
# .agent Documentation Index

**version:** v1.0.0  
**Last Updated:** [Current Date]  
**Project:** [Project Name]

## Purpose
This file serves as the master index for all AI agent documentation. Read this first before implementing any features to understand available context.

## Quick Start
1. For new features: Review relevant **System** docs and **Tasks** for similar implementations
2. For specific processes: Check **SOPs** for step-by-step guides
3. When stuck: Search this index for related documentation

---

## Project Status
**Stage:** Initial Setup  
**Total Documents:** 0 system docs, 0 SOPs, 0 tasks  
**Last Feature:** None yet

---

## System Documentation
*System documentation will be created as the project architecture develops*

### Planned System Docs:
- `architecture.md` - Will document project structure as it's built
- `database-schema.md` - Will document database design when implemented
- `api-endpoints.md` - Will document API routes as they're created
- `tech-stack.md` - Will track dependencies and versions

---

## Standard Operating Procedures (SOPs)
*SOPs will be created as development patterns emerge*

### Recommended Initial SOPs to Create:
- `adding-feature.md` - Process for adding new features
- `running-tests.md` - How to run and write tests
- `git-workflow.md` - Branch strategy and commit conventions
- `deployment.md` - Deployment process when established

---

## Implementation Tasks
*This section will populate as features are implemented*

---

## Documentation Maintenance

### When to Update
- **After completing any feature** → Run `/update-doc` to save implementation plan
- **After correcting agent mistakes** → Run `/update-doc generate SOP for [process]`
- **After architectural changes** → Update `system/architecture.md`
- **After schema changes** → Update `system/database-schema.md`
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

*This index will grow as the project develops. Keep it updated and organized.*
```

### 3.4 Create Initial .gitignore
Based on tech stack, generate appropriate .gitignore:
- Node.js: node_modules, .env, dist, build, coverage
- Python: venv, __pycache__, .env, *.pyc
- Common: .DS_Store, .idea, .vscode, *.log

Ensure `.agent/`, `.claude/`, and `archive/` are tracked (not ignored).

### 3.5 Create Starter SOPs

#### .agent/sops/git-workflow.md
```markdown
# SOP: Git Workflow

**version:** v1.0.0  
**Created:** [Date]

## When to Use
Every time you commit code to this repository

## Process
1. Create feature branch: `git checkout -b feature/[feature-name]`
2. Make changes and test locally
3. Stage changes: `git add .`
4. Commit with conventional commit format:
   - `feat: add new feature`
   - `fix: resolve bug`
   - `docs: update documentation`
   - `refactor: restructure code`
   - `test: add tests`
   - `chore: update dependencies`
5. Push to remote: `git push origin feature/[feature-name]`
6. Create pull request (if team project)
7. Merge to main after review

## Related Documentation
- CLAUDE.md - Code style guidelines

## Common Mistakes
- **Mistake:** Committing directly to main
  - **Solution:** Always use feature branches
- **Mistake:** Vague commit messages
  - **Solution:** Use conventional commits format
```

#### .agent/sops/project-setup.md
```markdown
# SOP: Project Setup for New Developers

**version:** v1.0.0  
**Created:** [Date]

## When to Use
When setting up development environment for the first time

## Prerequisites
- [Runtime] installed (version [X])
- [Package manager] installed
- Git installed and configured
- GitHub access to repository

## Process
1. Clone repository:
   \`\`\`bash
   git clone [repository-url]
   cd [project-name]
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   [install-command]
   \`\`\`

3. Set up environment variables:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your local configuration
   \`\`\`

4. [Database setup if applicable]:
   \`\`\`bash
   [database-commands]
   \`\`\`

5. Run tests to verify setup:
   \`\`\`bash
   [test-command]
   \`\`\`

6. Start development server:
   \`\`\`bash
   [start-command]
   \`\`\`

## Related Documentation
- CLAUDE.md - Common commands
- system/tech-stack.md - Technology requirements

## Common Mistakes
- **Mistake:** Forgetting to copy .env.example
  - **Solution:** Always create .env before running app
```

## Phase 4: Initial Git Commit

### 4.1 Create Initial Commit
```bash
# Stage all files
git add .

# Initial commit
git commit -m "chore(init): initialize project with .agent documentation system v1.0.0

- Set up .agent folder structure (tasks, system, sops)
- Configure CLAUDE.md with project guidelines
- Create update-doc command for automated documentation
- Establish Git automation workflow
- Add initial SOPs for git workflow and project setup
- Configure versioning system"

# Push to remote (if configured)
git push -u origin main
```

### 4.2 Create README.md (if doesn't exist)
```markdown
# [Project Name]

[Brief description from user input]

## Tech Stack
- [List of technologies]

## Getting Started
See [.agent/sops/project-setup.md](.agent/sops/project-setup.md) for detailed setup instructions.

## Documentation
This project uses an AI-optimized documentation system in the `.agent/` folder. See [.agent/README.md](.agent/README.md) for more information.

## Development
[Will be populated as project develops]

## License
[License type]
```

## Phase 5: Validation & Next Steps

### 5.1 Verify Setup
Confirm:
- [ ] `.agent/` folder structure created
- [ ] `CLAUDE.md` exists with version v1.0.0
- [ ] `.agent/README.md` created with master index
- [ ] `update-doc.md` command configured
- [ ] Initial SOPs created (git-workflow, project-setup)
- [ ] `.gitignore` configured appropriately
- [ ] Git initialized and first commit made
- [ ] Remote configured (if URL provided)
- [ ] All files committed and pushed

### 5.2 Provide Summary
Generate summary including:
- ✅ Documentation system initialized at v1.0.0
- ✅ Git repository configured and committed
- ✅ Initial SOPs created: [list]
- ✅ Ready for development

### 5.3 Recommend Next Steps
1. **First feature**: Start with `/update-doc generate SOP for adding-feature` to establish your development workflow
2. **As you build**: Update `system/architecture.md` with your actual project structure
3. **Before each feature**: Read `.agent/README.md` for context
4. **After each feature**: Run `/update-doc` to document

## Expected Outcome

A new project with:
- ✅ Complete .agent documentation infrastructure from day one
- ✅ Versioning system (semantic versioning starting at v1.0.0)
- ✅ Git automation for all documentation updates
- ✅ Archive folder for deprecated content
- ✅ Initial SOPs for common processes
- ✅ Master index for easy navigation
- ✅ Foundation for 50-60% context savings and 2-3x faster development

The project is now ready for efficient AI-assisted development with built-in documentation habits.

---

## Begin Implementation

Please proceed with gathering project information and setting up the .agent documentation system for this new project.

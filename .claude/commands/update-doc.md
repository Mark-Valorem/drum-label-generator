# Update Documentation Command

**version:** v1.0.0

## Purpose

Automate creation and maintenance of the .agent documentation system with version control.

## Commands

### Update After Feature Implementation

```
/update-doc
```

**Actions:**
1. Review recent conversation for completed work
2. If implementation plan exists, save to `tasks/[feature-name].md`
3. Identify repeatable processes, create/update SOPs in `sops/`
4. Update `README.md` and increment patch version (v1.0.0 → v1.0.1)
5. Move any unused/deprecated files to `archive/` preserving folder structure
6. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "docs: update documentation system to v${version}"
   git push origin main
   ```
7. Provide summary of all updates made

### Generate Specific SOP

```
/update-doc generate SOP for [process name]
```

**Actions:**
1. Create SOP document in `sops/[process-name].md`
2. Include standard SOP structure (see below)
3. Update `README.md` index and increment version
4. Move any deprecated docs to `archive/` with timestamp
5. Commit and push to GitHub with descriptive message
6. Confirm SOP created and indexed

### Major Documentation Refactor

```
/update-doc major
```

**Actions:**
1. Increment major version (v1.0.0 → v2.0.0)
2. Review all documentation for accuracy
3. Archive outdated content
4. Restructure if needed
5. Commit with "docs(major): " prefix

## SOP Document Structure

```markdown
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
```

## Versioning Rules

- **Patch (v1.0.0 → v1.0.1)**: Minor updates, new SOPs, small corrections
- **Minor (v1.0.0 → v1.1.0)**: New major features documented, significant SOPs added
- **Major (v1.0.0 → v2.0.0)**: Complete documentation restructure, breaking changes

## Archiving Rules

When moving files to `archive/`:
1. Preserve original folder structure: `archive/[date]/[original-path]`
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

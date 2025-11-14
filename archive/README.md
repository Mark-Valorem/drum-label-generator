# Archive Folder

**Created:** 2025-11-14

## Purpose

This folder contains deprecated, outdated, or superseded files from the project. Files are archived rather than deleted to maintain project history and enable recovery if needed.

## Structure

Archived files preserve their original folder structure with date stamps:

```
archive/
└── YYYY-MM-DD/
    ├── original-folder-path/
    │   └── deprecated-file.ext
    └── ARCHIVE_NOTES.md
```

## Archiving Process

When files are archived:

1. **Create dated subfolder:** `archive/YYYY-MM-DD/`
2. **Preserve path structure:** Maintain original relative path
3. **Add archive notes:** Document reason for archiving
4. **Update references:** Remove from active documentation
5. **Commit changes:** Include in version control

## Archive Notes Format

Each archive date folder should contain `ARCHIVE_NOTES.md`:

```markdown
# Archive Notes - YYYY-MM-DD

## Archived Files

### path/to/file.ext
- **Reason:** [Why file was archived]
- **Replaced by:** [New file/approach if applicable]
- **Date archived:** YYYY-MM-DD
- **Safe to delete:** Yes/No (and when)

## Context

[Additional context about why these files were archived]
```

## Recovery

To recover archived files:

1. Navigate to appropriate date folder
2. Copy file back to original location
3. Update documentation references
4. Consider if file needs updates before use

## Retention Policy

**Indefinite retention** for:
- Code files (historical reference)
- Documentation (context preservation)
- Configuration (rollback capability)

**Review after 1 year:**
- Temporary test files
- Duplicate data files
- Superseded scripts

## Current Status

**Total archives:** 0
**Last archived:** Never

---

*This folder is currently empty. Files will be added here as the project evolves.*

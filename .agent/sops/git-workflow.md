# SOP: Git Workflow

**version:** v1.0.0
**Created:** 2025-11-14
**Last Updated:** 2025-11-14

## When to Use

Every time you commit code or documentation to this repository.

## Prerequisites

- Git installed and configured
- GitHub repository access (if using remote)
- Understanding of conventional commit format

## Process

### 1. Create Feature Branch

```bash
git checkout -b feature/[feature-name]
```

**Examples:**
- `feature/add-multi-page-layout`
- `feature/unleashed-api-integration`
- `feature/custom-barcode-formats`

### 2. Make Changes and Test

- Edit code/documentation
- Test locally with `python drum_label_generator.py sample_data.csv`
- Run validation: `python test_installation.py`
- Verify output PDFs in `output/` folder

### 3. Stage Changes

```bash
git add .
```

Or stage specific files:
```bash
git add drum_label_generator.py config.py
```

### 4. Commit with Conventional Format

**Format:** `<type>: <description>`

**Types:**
- `feat:` - New feature (e.g., "feat: add support for multiple labels per page")
- `fix:` - Bug fix (e.g., "fix: resolve barcode scanning issue with special characters")
- `docs:` - Documentation changes (e.g., "docs: update README with new data format")
- `refactor:` - Code restructuring without feature changes (e.g., "refactor: extract label section rendering to separate methods")
- `test:` - Adding or modifying tests (e.g., "test: add validation for missing GHS pictograms")
- `chore:` - Maintenance tasks (e.g., "chore: update dependencies to latest versions")

**Examples:**
```bash
git commit -m "feat: add support for custom QR code URLs"
git commit -m "fix: handle missing expiry_date gracefully"
git commit -m "docs: update CLAUDE.md with new compliance requirements"
```

### 5. Push to Remote

```bash
# First time for new branch
git push -u origin feature/[feature-name]

# Subsequent pushes
git push origin feature/[feature-name]
```

### 6. Create Pull Request (if team project)

- Navigate to GitHub repository
- Click "New Pull Request"
- Select your feature branch
- Add description of changes
- Request review

### 7. Merge to Main

**After approval:**
```bash
git checkout main
git merge feature/[feature-name]
git push origin main
```

**Or use GitHub's merge button**

### 8. Clean Up Branch

```bash
git branch -d feature/[feature-name]
git push origin --delete feature/[feature-name]
```

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Code style guidelines
- [project-setup.md](project-setup.md) - Development environment setup

## Common Mistakes

### Mistake: Committing directly to main
**Solution:** Always use feature branches for new work. Only commit directly to main for hotfixes or documentation updates.

### Mistake: Vague commit messages
**Bad:** `git commit -m "updates"`
**Good:** `git commit -m "feat: add emergency contact field to label layout"`

**Solution:** Use conventional commits format with clear, descriptive messages.

### Mistake: Forgetting to test before committing
**Solution:** Always run test suite and generate sample labels before committing changes.

### Mistake: Committing sensitive data
**Solution:**
- Check `.gitignore` includes sensitive files
- Never commit actual customer data, API keys, or credentials
- Use `sample_data.csv` for examples only

### Mistake: Not updating documentation
**Solution:** When adding features, update relevant docs and run `/update-doc`

## Example Workflow

```bash
# 1. Start new feature
git checkout main
git pull origin main
git checkout -b feature/add-expiry-warning

# 2. Make changes
# ... edit drum_label_generator.py ...

# 3. Test
python test_installation.py
python drum_label_generator.py sample_data.csv

# 4. Stage and commit
git add drum_label_generator.py config.py
git commit -m "feat: add red warning box for expired products"

# 5. Push
git push -u origin feature/add-expiry-warning

# 6. Create PR on GitHub, get approved, merge

# 7. Clean up
git checkout main
git pull origin main
git branch -d feature/add-expiry-warning
```

## Version Tagging

When releasing new versions:

```bash
# Tag the release
git tag -a v1.1.0 -m "Release v1.1.0: Add multi-page layout support"

# Push tag to remote
git push origin v1.1.0
```

**Versioning scheme:**
- v1.0.0 - Major.Minor.Patch
- Major: Breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes

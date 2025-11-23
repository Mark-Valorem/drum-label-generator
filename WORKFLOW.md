# Project Workflow Commands

## 1. START A NEW TASK
**Copy/Paste this into Claude when you begin work:**
> "I am starting a new task: [DESCRIBE TASK HERE].
> 1. First, read `.claude_docs/MEMORY.md` to understand the rendering rules.
> 2. Create a new git branch named `[feature-name-here]`.
> 3. Tell me when you are ready for instructions."

---

## 2. FINISH & DOCUMENT (The "Memory Bank" Update)
**Copy/Paste this when the code is working:**
> "The task is complete and verified. Please wrap up:
> 1. Update `.claude_docs/MEMORY.md`: Record any new rules or architectural decisions we made.
> 2. Update `.claude_docs/PROGRESS.md`: Log this task under the current version.
> 3. Run `git add .`
> 4. Generate a commit message following conventional commits (e.g., 'feat:', 'fix:') and commit the changes."

---

## 3. MERGE & SAVE (The "Safe" Way)
**Copy/Paste this to save everything to the main cloud:**
> "I am ready to merge.
> 1. Switch back to `main`.
> 2. Merge the current branch into `main`.
> 3. Push `main` to origin.
> 4. Delete the old feature branch locally."
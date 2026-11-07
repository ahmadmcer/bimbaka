# AGENTS.md - bimbaka

Operating guidelines and workflow specifications for AI coding assistants.

## Project Overview & Tech Stack
- **Archetype:** Fullstack Web Application (Django)
- **Stack:** Python 3.12, Django 6.0.1, PostgreSQL / SQLite, Gunicorn, Whitenoise, Scikit-learn, Pandas.
- **Manifests:** `requirements.txt`, `pyproject.toml`, `Procfile`, `.python-version`.
- **Primary Apps:** `bimbaka` (core configuration), `belajar` (business logic, models, views, templates).

## Operational Commands
- **Install dependencies:** `pip install -r requirements.txt`
- **Build application:** Zero-build runtime (no build required for interpreted Python backend)
- **Run dev server:** `python manage.py runserver`
- **Run full test suite:** `pytest` or `python manage.py test`
- **Run single test:** `pytest <path_to_test>::<test_name>` or `python manage.py test <path_to_test>`
- **Lint code:** `djlint . --reformat` and `black .`
- **Type check:** `mypy .`
- **Database migrations:** `python manage.py makemigrations && python manage.py migrate`

## Code Style & Architectural Conventions
- Enforce Django MTV (Model-Template-View) layer separation across all apps.
- Keep view functions and class-based views lean; encapsulate domain logic in models or service modules.
- Ensure form validation and model fields define explicit constraints, help texts, and error handling.
- Co-locate HTML templates within the corresponding app directory (`belajar/templates/`).
- Format all Python files with `black` and Django templates with `djlint`.

## Boundaries & "Never Do" Rules
- Always create and switch to a separate branch before starting work; never work on `main`.
- Always commit small changes atomically with Conventional Commits messages.
- Always update `CHANGELOG.md` under `## [Unreleased]` for every functional modification.
- Always report discovered bugs or tech debt by opening a GitHub Issue (`gh issue create`) and tagging the affected line with an issue reference comment.
- Always merge into `main` exclusively via Pull Requests using `gh pr create` and `gh pr merge --merge --delete-branch`.
- Always delete completed feature/fix branches immediately after merging.
- Always tag releases with annotated git tags (`git tag -a vX.Y.Z -m "Release vX.Y.Z"`).
- Always delegate research, deep file scanning, and isolated subtasks to subagents.
- Never commit directly to the `main` branch.
- Never force merge (`--admin` bypass), force push (`git push -f`), or squash commits (`--squash` is strictly forbidden).
- Never leave merged or stale branches in local or remote repository.
- Never ignore discovered bugs or technical debt without creating a tracked GitHub Issue.
- Never commit secrets, passwords, `.env` files, or production credentials.

## Git & Development Workflow

### 1. Branch Strategy & Cleanup
- Always branch off updated `main`: `git checkout -b <type>/<description>`.
- Branch naming convention: `feat/<name>`, `fix/<name>`, `chore/<name>`, `docs/<name>`, `issue-<id>/<name>`.
- Merged branches must be deleted immediately:
  - Remote: Handled automatically by `gh pr merge --delete-branch`.
  - Local: `git checkout main && git pull origin main && git branch -d <branch_name>`.

### 2. Atomic Commits
- Commit every small, logical step independently. Do not batch multiple unrelated changes into one commit.
- Use Conventional Commits 1.0.0 syntax: `<type>(<scope>): <summary>`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
  - Example: `git commit -m "fix(belajar): correct student score calculation logic"`

### 3. Issue Tracking & Code Comments
- When a bug, limitation, or refactoring need is found:
  1. Create a GitHub Issue using GitHub CLI:
     ```bash
     gh issue create --title "<Issue summary>" --body "<Detailed description, file paths, steps to reproduce>" --label "bug"
     ```
  2. Note the generated Issue number (e.g. `#15`).
  3. Annotate the affected code line with a structured comment:
     ```python
     # TO-DO (#15): Refactor query optimization to prevent N+1 queries on student enrollment list
     ```
  4. Commit the comment annotation as an atomic commit (`chore: add issue annotation for #15`).

### 4. Pull Requests & Merge Policy
- Merging to `main` requires a Pull Request via GitHub CLI:
  ```bash
  gh pr create --title "<type>(<scope>): <Title>" --body "<Summary of changes, resolves #<id>>"
  ```
- **Merge Strategy (Strict):**
  - **Dilarang keras force merge dan squash.** Squash destroys fine-grained atomic commit history and bisectability.
  - Merge using merge commits:
    ```bash
    gh pr merge <PR_NUMBER> --merge --delete-branch
    ```

### 5. Changelog & Versioning Standard
- Follow Keep a Changelog 1.1.0 and Semantic Versioning 2.0.0.
- Every PR must update `CHANGELOG.md` under `## [Unreleased]` in the matching section:
  `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, or `Security`.
- On release cut:
  1. Move `## [Unreleased]` items to `## [X.Y.Z] - YYYY-MM-DD`.
  2. Add an empty `## [Unreleased]` section at top.
  3. Commit release: `git commit -m "chore(release): bump version to vX.Y.Z"`.
  4. Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
  5. Push commits and tags: `git push origin main && git push origin vX.Y.Z`.

### 6. Subagent Delegation Architecture
- Use subagent delegation to prevent context window bloat and reasoning degradation:
  - Delegate large-scale file searches, documentation exploration, and dependency auditing to `research` subagents.
  - Delegate isolated module implementations and unit test writing to specialized worker subagents.
  - The parent orchestrator reviews output, verifies tests, coordinates atomic commits, and manages PR lifecycles.

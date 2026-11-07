# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-08

### Added
- Created `AGENTS.md` establishing standardized guidelines for AI coding agents, including atomic commit enforcement, strict branch isolation, issue tracking, and PR merge rules (scored 100/100 Gold Tier).
- Created administrative functions for quiz management and student records in `belajar` app.
- Added edit and delete functionality for quiz components (`kuis`).
- Documented full historical development lineage from initial prototype to production release.

### Changed
- Standardized project configuration and updated Python version requirement to 3.12.
- Updated dependencies to modern stable versions: Django 6.0.1, scikit-learn 1.6.1, pandas 2.2.2.
- Improved teacher profile editing workflow (`edit profile guru`).

### Removed
- Cleaned up obsolete machine learning model files and legacy model directories.
- Removed unused static assets and redundant files to maintain a lean production footprint.

## [0.4.0] - 2026-02-26

*Catatan: Versi ini dan sebelumnya dikembangkan pada repositori fondasi [nawawwow/bimbaka](https://github.com/nawawwow/bimbaka).*

### Added
- Machine learning model training pipeline and automated dataset generation (`belajar/ml_models/`).
- Automated code formatting using `black` and template linting using `djlint` via `pyproject.toml`.

### Changed
- Consolidated and refactored database migrations for `Kuis`, `RiwayatKuis`, and `SoalKuis` (PR #4).
- Hardened Django settings for production deployment on Railway (`ALLOWED_HOSTS`, `DEBUG`, `SECURE_PROXY_SSL_HEADER`) (PR #3).
- Updated core package dependencies in `requirements.txt` (PR #2).

## [0.3.0] - 2025-12-25

### Added
- Comprehensive student evaluation models (`NilaiEvaluasi`, `JawabanEvaluasi`) and evaluation result page (`hasil_evaluasi.html`).
- Interactive drag-and-drop mechanics for learning quizzes.
- Personalized material recommendations engine based on evaluation outcomes.
- Teacher and student dashboards (`dashboard_guru`, `dashboard_siswa`) with learning statistics.
- User profile update capabilities.

### Changed
- Streamlined navigation by removing standalone evaluation link in favor of integrated assessment flows.

## [0.2.0] - 2025-10-30

### Added
- Grade-based learning curricula structure for Kelas 2 and Kelas 3.
- Pretest question sets and answer keys in PDF, Markdown, and HTML formats.
- Class level selection during student user registration.
- Detailed material pages with dynamic routing per grade level.

### Changed
- Redesigned main landing page (`beranda.html`) for enhanced interactivity and responsiveness.
- Refactored `Materi` models and views to support hierarchical grade structures.

### Fixed
- Corrected multiplication formulas and arithmetic examples in grade 2 and grade 3 resources.

## [0.1.0] - 2025-09-25

### Added
- Initial project architecture (`bimbaka`) and primary application module (`belajar`).
- User authentication infrastructure (login, registration, logout, session management).
- Practice and assessment result views with responsive UI layouts.
- Cloud hosting deployment configurations for Railway using Gunicorn, Whitenoise, and `dj-database-url`.

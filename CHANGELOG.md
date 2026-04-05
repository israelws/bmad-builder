# Changelog

## [1.4.0] - 2026-03-29

### 🎁 Features

* **Standalone self-registering modules** — Single-skill modules no longer need a dedicated `-setup` skill. The Module Builder auto-detects single vs multi-skill input and embeds registration directly in the skill via `assets/module-setup.md`. First-run init hooks into existing agent memory detection for a unified setup experience
* **Module Builder skill** — New `bmad-module-builder` with three capabilities: Ideate Module (IM) for creative brainstorming, Create Module (CM) for scaffolding both standalone and multi-skill modules, and Validate Module (VM) for structural and quality validation with `--headless` CI support
* **BMB Setup skill** — Extracted and regenerated as `bmad-bmb-setup` using the Module Builder itself. Manages config.yaml, config.user.yaml, and module-help.csv with anti-zombie merge pattern and legacy migration
* **Workflow Convert capability (CW)** — One-command skill modernization via `--convert <path-or-url>`. Produces a clean BMad-compliant equivalent with an interactive HTML before/after comparison report including token metrics, categorized changes, and dark/light mode
* **Script creation standards** — Formalized Python-first policy with PEP 723 metadata, cross-platform portability via `uv run`, and explicit user approval for external dependencies

### 🐛 Bug Fixes

* Fix HTML quality report data injection — template used `const RAW` but generator looked for `const DATA`, causing broken report rendering in both builders
* Fix merge-help-csv.py HEADER schema — synced from 15 columns to canonical 13-column schema, preventing silent CSV corruption during module setup
* Fix `{project-root}` path validation overcorrection — scanner incorrectly rejected valid project-scope paths like `{project-root}/docs/report.md`
* Add bmad-module-builder to marketplace.json — skill was merged but not registered in the plugin manifest

### ♻️ Refactoring

* **Outcome-driven builder overhaul** — Reframe both builders around discovery-first design: existing skill input treated as reference material, 3-way routing (Analyze/Edit/Rebuild), pruning check in Phase 4, "Quality Optimizer" renamed to "Quality Analysis". Net 44% token reduction in Workflow Builder Phase 5 context
* **Ideation restructured into 7 phases** — Module identity locked in Phase 1, new Phase 6 capability review with user, mandatory config section, self-contained skill briefs, writing discipline (raw ideas in phases 1-2, structured from phase 3+)
* Consolidate plugin.json metadata into marketplace.json — single source of truth for plugin metadata
* Remove npm publishing pipeline — distribution now via `.claude-plugin/` manifest

### 📚 Documentation

* **Comprehensive docs overhaul** — Quick start guide with `bmad-bmb-setup` registration, full 13-column CSV guide explaining how `bmad-help` uses each column, "Distribution: Plugins and Marketplaces" section covering 43+ skills platforms, standalone vs multi-skill patterns throughout all docs
* Add personal-use guidance — users can copy skill folders directly to their tool's skills directory without module packaging
* Remove deprecated bmad-init references from workflow-patterns docs
* New explanation doc: Scripts in Skills — design patterns for deterministic scripting

### 🔧 Maintenance

* Bump version to 1.4.0 across package.json and marketplace.json
* Remove npm release scripts and publishConfig from package.json

## [1.1.0] - 2026-03-19

### Changed

- Flatten skill folder structure to align with Agent Skills spec
- Replace bmad-init dependency with direct config loading
- Optimize workflow-builder and agent-builder skills

### Improved

- Optimizer now captures all fragments in report and produces a final HTML report

### Removed

- Obsolete sample files from old skill structure
- Unneeded images from project root

## [1.0.0] - 2026-03-15

### Release

First official v1 release of BMad Builder — a standard skill-compliant factory for creating BMad Agents, Workflows, and Modules.
The module specific skill is coming soon pending alignment on final format with skill transition.

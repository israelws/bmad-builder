---
title: "Product Brief: BMAD Next-Gen Installer"
status: "complete"
created: "2026-03-12"
updated: "2026-03-12"
inputs:
  - "User brain dump (BMad)"
  - "Current installer codebase analysis (tools/cli/)"
  - "Vercel skills CLI README (github.com/vercel-labs/skills)"
  - "Web research: AI agent skills ecosystem, marketplace landscape"
---

# Product Brief: BMAD Next-Gen Installer

## Executive Summary

The BMAD Method has grown from a developer-focused agile AI methodology into a framework used across 20+ platforms — but its installer hasn't kept up. Today, every new AI tool that supports skills means manual work: adding platform configs, maintaining directory mappings, testing installation paths. This doesn't scale, and it locks BMAD out of the fastest-growing segment of the market: non-technical users on low-code and UI-based platforms.

The Next-Gen Installer replaces BMAD's monolithic Node.js CLI with a skill-based architecture built on the emerging Agent Skills standard. By leveraging the open-source Vercel skills CLI for cross-platform installation and introducing a plugin system where BMAD modules are self-describing skill bundles, we eliminate the platform maintenance burden, open distribution beyond what BMAD could maintain alone, and lay the foundation for a marketplace where anyone — developers, creators, educators, therapists — can discover, download, and install BMAD plugins without needing Git, Node, or a terminal.

This isn't just a better installer. It's the infrastructure that transforms BMAD from a dev methodology into an open platform.

## The Problem

BMAD currently supports ~20 AI platforms through a custom Node.js installer that maintains per-platform directory mappings, template formats, and legacy migration paths. Every platform that changes its skill conventions — and they change constantly — requires installer updates, testing, and a new release. This is the single biggest maintenance burden on the bmad-code team.

Meanwhile, the Agent Skills ecosystem has exploded. The broader skills ecosystem now spans 40+ platforms with hundreds of thousands of skills and millions of installs. The market is moving fast, and BMAD is fighting to keep up with platform-by-platform manual support while new tools launch weekly.

Worse, the current installer requires Node.js and npm — a hard barrier for the growing population of non-technical users building with AI through UI-based platforms like Claude Co-Work. These users can't run `npx bmad-method install`. They need something simpler.

The cost of the status quo is clear: developer time spent maintaining platform configs instead of building methodology, and an entire user segment that can't access BMAD at all.

## The Solution

The Next-Gen Installer is a skill-based distribution and registration system with three layers:

**1. Self-Describing Plugins.** Every BMAD module becomes a plugin — a bundle of skills with a manifest that declares what's included, how skills relate to each other, what capabilities they provide, and how they integrate with the BMAD help system. The plugin format adopts the Anthropic plugin standard (used by Vercel and the broader skills ecosystem) as its base, extended with a BMAD-specific manifest (`bmad-manifest.json`) for metadata the base standard doesn't cover — such as installer options, capability declarations, and help system integration. A plugin is fully self-contained: download it, put the skills in your tool's skill folder, and it works.

**2. Cross-Platform Installation via Vercel Skills CLI.** For users who want an automated install experience, the installer builds on the MIT-licensed Vercel skills CLI, which handles translating the Anthropic plugin standard to 40+ platforms. The exact integration pattern — wrapping, forking, or calling as a dependency — is a PRD-level architecture decision. The strategic intent is clear: BMAD stops maintaining platform directory mappings and delegates that problem to a well-maintained open-source project. The Vercel dependency carries minor supply-chain risk, but the pros far outweigh it: the MIT license means BMAD can fork and maintain it if Vercel ever deprioritizes the project. Supporting many platforms is a core BMAD differentiator — we need this problem solved one way or another, and leveraging an existing solution beats building from scratch.

**3. Runtime Registration via `bmad-init`.** A global skill that scans for installed BMAD manifests, registers capabilities, configures project settings, and bootstraps the BMAD experience. Users run it once after installation. It replaces the current installer's config-collection step and provides the entry point for updates via `bmad-update`. Note: `bmad-init` itself must be installed before it can run — the NPX installer and zip bundle README handle this bootstrapping step by ensuring `bmad-init` is always included as a base skill.

For non-technical users, distribution is straightforward: download a zip containing all plugin skills plus a README with platform-specific guidance. The honest reality is that "copy to the right folder" still requires knowing where that folder is — and this varies by platform. The README provides per-platform instructions for the most common tools, and as the low-code/no-code AI platform space matures, we improve guidance and explore deeper integrations. We don't need to solve universal one-click install today, but we do need to be honest that the non-technical path has friction we'll reduce over time.

## What Makes This Different

**The anti-fragmentation layer.** The AI tooling space is fracturing across 40+ platforms with no shared methodology layer. BMAD is uniquely positioned to be the cross-platform constant — the structured approach that works the same in Cursor, Claude Code, Windsurf, Copilot, and whatever launches next month. Every other methodology or skill framework maintains its own platform support matrix. By building on the open-source skills CLI ecosystem, BMAD offloads the highest-churn maintenance burden and focuses on what actually differentiates it: the methodology itself.

**Methodology-backed quality in a sea of AI slop.** The broader skills ecosystem is flooded with low-quality, AI-generated content — and early research (Snyk, 2026) suggests a meaningful percentage of community skills contain security vulnerabilities. BMAD plugins are different: they're structured, tested, and part of a coherent methodology. The BMAD manifest system ensures skills work together, declare dependencies, and integrate with the help system. This is a curated ecosystem, not an open bazaar — all plugin submissions will be gated, reviewed, and curated by the BMAD creator and open-source core team. This human-reviewed quality gate is a key differentiator that becomes more valuable as the broader ecosystem grows noisier.

**Platform for everything, not just code.** No competitor in the AI skills space is building beyond software development workflows. BMAD's plugin architecture is domain-agnostic — the same manifest system, installer, and registration flow that powers the dev methodology will power creative, educational, therapeutic, and personal plugins built with the BMAD Builder. This is unaddressed whitespace in the current market.

## Who This Serves

**BMAD Open-Source Contributors and Module Authors** (primary v1 target) — The people who build BMAD modules today. They currently package workflows and agents manually and rely on the installer team to support new platforms. They need a standardized way to package modules as self-contained skill plugins that work anywhere — and they need to do it without waiting on installer changes. Success: a module author can package, test, and distribute a plugin independently.

**Developers Using AI Coding Tools** — Technical users across Claude Code, Cursor, Gemini CLI, Codex, and dozens of other platforms who want to install BMAD with a single command and have it just work, regardless of their tool. Success: `npx` one-liner installs BMAD to their tool of choice, and `bmad-init` configures it for their project.

**Non-Technical AI Users** — People building with AI through UI-based platforms who don't have (or want) a development environment. They need download-and-copy simplicity with clear, platform-specific guidance. This is an emerging segment — we don't fully understand their needs yet, but removing the Node.js barrier opens BMAD to product managers, designers, educators, and knowledge workers who currently cannot access it. Success: a user who has never opened a terminal can install and use BMAD on their platform.

**Future Plugin Creators** — People who will build BMAD-compatible plugins for domains beyond software development. They need a distribution system that gets their work into users' hands without building their own installer. Success: a non-dev plugin author can package and share their creation using the same manifest and distribution system.

## Success Criteria

- **Platform maintenance burden reduced dramatically:** Custom platform directory code in BMAD's codebase approaches zero, with cross-platform installation delegated to the skills CLI ecosystem
- **Broad platform coverage:** Installation verified on the top platforms by install volume, with the skills CLI handling the long tail
- **Non-technical installation path exists:** Users can install BMAD without Node.js, npm, or Git — validated by at least testing the flow with non-developer users
- **Plugin self-registration works:** `bmad-init` correctly discovers and registers all installed BMAD plugins from manifests alone, with clear error messages for malformed or missing manifests
- **Module authors can package and distribute plugins** using the manifest system without needing installer changes — validated by at least one external module author successfully publishing a plugin
- **Update path exists:** `bmad-update` allows users to update installed plugins without reinstalling from scratch
- **Migration from current installer:** Existing BMAD users on the Node.js CLI have a clear, documented path to the next-gen system

## Scope

**In scope for the next-gen installer:**
- Plugin manifest format (`bmad-manifest.json`) and specification
- `bmad-init` skill for runtime discovery and registration
- `bmad-update` skill for plugin updates
- Integration with Vercel skills CLI (or equivalent) for automated cross-platform installation
- NPX-based installer for technical users
- Downloadable zip bundles with platform-specific README guidance for non-technical users
- Migration path from current installer — existing users need a clear upgrade story, whether that's a migration command or documented manual steps

**Explicitly out of scope:**
- BMAD Builder (plugin creation tool) — separate initiative
- Marketplace platform (web-based discovery and download) — future phase
- Converting existing workflows/agents to skills — prerequisite, handled separately
- One-click install for every platform — emerging space, guidance-based for now
- Monetization or paid plugin infrastructure
- Plugin quality certification process — the review and curation workflow will be defined separately, though the gated-submission principle is a core architectural requirement

## Vision

If the next-gen installer succeeds, BMAD becomes the first AI agent methodology that is truly platform-agnostic and accessible to non-developers. The plugin architecture creates the foundation for a marketplace where a therapist can download a "Guided Journaling" BMAD plugin, a game designer can install a "World Building" plugin, and a startup founder can get the full software development methodology — all through the same system, on whatever AI platform they use.

In 2-3 years, BMAD plugins become a leading way people package and share structured AI agent workflows. The combination of methodology-backed quality, cross-platform portability, and open distribution creates a flywheel: more plugins attract more users across more platforms, more users attract more plugin creators from more domains, and the growing library of quality plugins reinforces BMAD's reputation as the curated alternative to the skills bazaar. BMAD evolves from a method into an ecosystem.

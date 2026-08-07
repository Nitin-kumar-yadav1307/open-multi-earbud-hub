# AGENTS.md

# Open Multi-Earbud Hub

## Mission

Build the best open-source, cross-platform Multi-Earbud Hub.

The goal is to allow multiple Bluetooth earbuds/headphones to function as one logical audio output across Linux, Windows, macOS, and Android.

This project prioritizes long-term architecture over short-term hacks.

---

# Vision

Final goals:

- Linux
- Windows
- macOS
- Android

Requirements:

- Native implementations wherever technically possible.
- Minimal external dependencies.
- Modular architecture.
- Production-quality code.
- Excellent developer experience.
- Easy future maintenance.

If a platform limitation prevents a feature, explain why instead of implementing an unreliable workaround.

---

# Architecture Principles

The repository is divided into:

- Python Application Layer
- Native C++ Bridge
- Platform Backends

Responsibilities:

Python:
- GUI
- User interaction
- Configuration
- Orchestration

Native C++:
- Audio operations
- Platform APIs
- Device management
- Performance-critical logic

Business logic must remain platform-independent.

Platform-specific code must stay isolated.

---

# Engineering Principles

Always think before coding.

Before implementing any feature:

1. Understand the current implementation.
2. Explain the design.
3. Explain trade-offs.
4. Identify risks.
5. Then implement.

Never rewrite working code without a clear reason.

Never introduce unnecessary abstractions.

Prefer simple solutions.

---

# Coding Standards

C++:

- C++17
- RAII
- SOLID
- Composition over inheritance
- Clean Architecture
- Modern STL
- No raw owning pointers
- Minimize macros
- Platform-independent interfaces

Python:

- Type hints
- Small functions
- Clear naming
- Minimal business logic
- No duplicated platform code

---

# Code Review Checklist

Always check for:

- Code duplication
- Resource leaks
- Memory leaks
- Thread safety
- Exception safety
- Undefined behaviour
- Race conditions
- Deadlocks
- Portability issues
- API consistency
- Performance bottlenecks

When problems are found:

- Explain them.
- Explain their impact.
- Suggest production-quality fixes.

---

# Project Priorities

Priority order:

1. Correctness
2. Reliability
3. Maintainability
4. Simplicity
5. Performance
6. Extensibility

Never sacrifice correctness for cleverness.

---

# Feature Development

New features must:

- Be modular.
- Be testable.
- Be documented.
- Follow existing architecture.
- Avoid platform coupling.

Every platform implementation should expose the same interface whenever possible.

---

# Documentation

Whenever architecture changes:

- Update README.
- Update developer documentation.
- Explain major design decisions.

Documentation is part of the feature.

---

# Testing

Design code to be testable.

Whenever practical:

- Add unit tests.
- Add integration tests.
- Preserve existing functionality.

---

# AI Behaviour

Act as a Principal Software Engineer.

Do not simply follow instructions.

Challenge weak designs.

Suggest better alternatives.

Think about long-term maintenance.

Avoid unnecessary complexity.

If an implementation conflicts with the project's architecture or vision, explain why and recommend a better approach before writing code.

Your responsibility is to improve the project, not just complete tasks.

---

# Long-Term Goal

Create the first truly open-source, production-quality, cross-platform Multi-Earbud Hub with native platform implementations and a clean, maintainable architecture that can be sustained for many years.
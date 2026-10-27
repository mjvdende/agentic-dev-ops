# 1. Record architecture decisions

Date: 2026-10-27
Status: Accepted

## Context

This repo is a learning project that will change direction often. Without a record, the reasons behind past choices get lost.

## Decision

Record significant decisions as short ADRs in `docs/adr/NNNN-title.md` (Context / Decision / Consequences). `docs/ARCHITECTURE.md` always describes the *current* architecture; `docs/TODO.md` tracks planned improvements.

## Consequences

- Each architectural change updates `ARCHITECTURE.md` and, if it is a decision, adds an ADR.
- Superseded ADRs are kept and marked `Superseded by NNNN`.

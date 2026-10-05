# ADR 0001: the shape of one run
- Status: accepted
- Date: 2026-10-05

## Context
Evaluated chain vs loop; chain used 3 calls per run in the offline environment.

## Decision (`decision`)
we keep the chain in agent.py

## Options considered (`options_considered`)
1. chain
2. loop

## Why not the other option (`why_not`)
The loop added extra complexity without improving accuracy on the offline fake model tests.

## What would reverse it (`reverses_it`)
when a question needs more than 2 model calls in 10 of the golden cases.
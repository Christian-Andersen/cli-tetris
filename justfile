alias c := check
alias r := run

[private]
default:
    @just --list

check:
    uv run -- prek run --all-files

run *args:
    uv run -- main.py {{ args }}

audit:
    uv run -- prek run audit

ci:
    uv run -- prek run --all-files --stage manual

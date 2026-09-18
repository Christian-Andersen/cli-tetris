alias c := check
alias r := run
alias ci := continuous_integration

[private]
default:
    @just --list

check:
    uv run -- prek run --all-files

run *args:
    uv run -- main.py {{ args }}

audit:
    uv run -- prek run audit

continuous_integration:
    uv run -- prek run --all-files --stage manual

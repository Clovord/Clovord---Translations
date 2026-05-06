from __future__ import annotations

import argparse
from pathlib import Path

CODEOWNERS_CANDIDATES = (
    Path(".github/CODEOWNERS"),
    Path("CODEOWNERS"),
    Path("docs/CODEOWNERS"),
)


def pattern_covers(pattern: str, required_path: str) -> bool:
    p = pattern.strip()
    r = required_path.strip().lstrip("/")
    if not p or not r:
        return False

    p = p.lstrip("/")

    if p in {"*", "**"}:
        return True

    if p.endswith("/**"):
        prefix = p[:-3]
        return r.startswith(prefix)

    if p.endswith("*"):
        prefix = p[:-1]
        return r.startswith(prefix)

    if p.endswith("/"):
        return r.startswith(p)

    return r == p or r.startswith(f"{p}/")


def file_has_covering_rule(codeowners_path: Path, required_path: str) -> bool:
    for raw_line in codeowners_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if not parts:
            continue

        pattern = parts[0]
        if pattern_covers(pattern, required_path):
            return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure CODEOWNERS covers a required path.")
    parser.add_argument("--repo-dir", required=True, help="Path to repository root")
    parser.add_argument("--required-path", required=True, help="Path that must be covered in CODEOWNERS")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)
    required_path = args.required_path.strip().lstrip("/")

    found_any = False
    for rel in CODEOWNERS_CANDIDATES:
        candidate = repo_dir / rel
        if not candidate.exists():
            continue

        found_any = True
        if file_has_covering_rule(candidate, required_path):
            print(f"CODEOWNERS coverage OK in {rel} for {required_path}")
            return 0

    if not found_any:
        print("CODEOWNERS not found in supported locations (.github/CODEOWNERS, CODEOWNERS, docs/CODEOWNERS)")
    else:
        print(f"No CODEOWNERS rule covers required path: {required_path}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

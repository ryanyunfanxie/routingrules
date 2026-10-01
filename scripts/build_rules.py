#!/usr/bin/env python3
"""Build client-specific selective routing rules from both regional manifests."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    ROOT / "config" / "services_hk.json",
    ROOT / "config" / "services_cn.json",
)
DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported schema_version")
    slug = manifest.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9_]+(?:-[a-z0-9_]+)*", slug):
        raise ValueError("slug must be a lowercase identifier using letters, digits, underscores, and hyphens")
    region = manifest.get("region")
    if not isinstance(region, str) or not re.fullmatch(r"[a-z0-9-]+", region):
        raise ValueError("region must be a lowercase identifier")
    services = manifest.get("services")
    if not isinstance(services, list) or not services:
        raise ValueError("services must be a non-empty list")

    seen_services: set[str] = set()
    seen_domains: set[str] = set()
    for service in services:
        service_id = service.get("id")
        if not service_id or service_id in seen_services:
            raise ValueError(f"Duplicate or missing service id: {service_id!r}")
        seen_services.add(service_id)
        if service.get("status") not in {
            "confirmed_region_restricted",
            "user_provided_operational",
            "region_sensitive",
        }:
            raise ValueError(f"Unsupported service status: {service_id}")
        domains = service.get("domains")
        if not isinstance(domains, list) or not domains:
            raise ValueError(f"Missing domains for {service_id}")
        for domain in domains:
            if domain != domain.lower() or not DOMAIN_RE.fullmatch(domain):
                raise ValueError(f"Invalid lowercase domain {domain!r} in {service_id}")
            if domain in seen_domains:
                raise ValueError(f"Duplicate domain: {domain}")
            seen_domains.add(domain)
    return manifest


def json_dump(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_shadowrocket(manifest: dict, source: Path, output: Path) -> None:
    policy = manifest["shadowrocket_policy"]
    lines = [
        f"# {manifest.get('display_name', manifest['name'])}",
        "# Selective rules: only matched services use the proxy.",
        f"# Generated from {source.relative_to(ROOT).as_posix()}; checked {manifest['last_checked']}.",
        "# Set the policy name below to the policy/group name in Shadowrocket.",
        "",
    ]
    for service in manifest["services"]:
        lines.append(f"# {service['name']}")
        lines.extend(f"DOMAIN-SUFFIX,{domain},{policy}" for domain in service["domains"])
        lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_v2rayn(manifest: dict, output: Path) -> None:
    outbound = manifest["v2rayn_outbound_tag"]
    rules = []
    for service in manifest["services"]:
        rules.append(
            {
                "port": "",
                "outboundTag": outbound,
                "enabled": True,
                "domain": [f"domain:{domain}" for domain in service["domains"]],
                "remarks": service["name"],
            }
        )
    json_dump(rules, output)


def build_index(manifests: list[dict], output: Path) -> None:
    sections = []
    for manifest in manifests:
        service_rows = []
        for service in manifest["services"]:
            links = " ".join(
                f'<a href="{html.escape(source["url"], quote=True)}">source</a>'
                for source in service["sources"]
            )
            service_rows.append(
                "<tr>"
                f"<td>{html.escape(service['name'])}</td>"
                f"<td><code>{html.escape(service['status'])}</code></td>"
                f"<td>{html.escape(service['reason'])}</td>"
                f"<td>{links}</td>"
                "</tr>"
            )
        slug = html.escape(manifest["slug"], quote=True)
        sections.append(
            f"""<h2>{html.escape(manifest.get('display_name', manifest['name']))}</h2>
<ul>
<li><a href="shadowrocket/{slug}.list">Shadowrocket rule set</a></li>
<li><a href="v2rayn/{slug}.json">v2rayN custom routing JSON</a></li>
</ul>
<table><thead><tr><th>Service</th><th>Status</th><th>Why included</th><th>Sources</th></tr></thead><tbody>{''.join(service_rows)}</tbody></table>"""
        )
    body = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>routingrules</title>
<style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}}code{{background:#f1f3f5;padding:.15rem .3rem;border-radius:.25rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;text-align:left;vertical-align:top}}a{{margin-right:.6rem}}</style>
<h1>routingrules</h1>
<p>Regional selective routing rules. Public, unauthenticated rule files; no node credentials or subscription tokens are included.</p>
{''.join(sections)}
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "public")
    args = parser.parse_args()

    manifests = [load_manifest(path) for path in MANIFESTS]
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for source, manifest in zip(MANIFESTS, manifests):
        slug = manifest["slug"]
        build_shadowrocket(manifest, source, output / "shadowrocket" / f"{slug}.list")
        build_v2rayn(manifest, output / "v2rayn" / f"{slug}.json")
    build_index(manifests, output / "index.html")
    (output / "availability.json").write_text(
        json.dumps(
            {
                "rulesets": [
                    {
                        "name": manifest["name"],
                        "display_name": manifest.get("display_name", manifest["name"]),
                        "slug": manifest["slug"],
                        "region": manifest.get("region"),
                        "description": manifest.get("description"),
                        "last_checked": manifest["last_checked"],
                        "services": manifest["services"],
                    }
                    for manifest in manifests
                ],
                "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

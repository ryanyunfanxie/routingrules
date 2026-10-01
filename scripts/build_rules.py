#!/usr/bin/env python3
"""Build client-specific selective routing rules from one canonical manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "services.json"
DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported schema_version")
    slug = manifest.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("slug must be a lowercase hyphenated identifier")
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
            "confirmed_hk_unsupported",
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


def build_shadowrocket(manifest: dict, output: Path) -> None:
    policy = manifest["shadowrocket_policy"]
    lines = [
        f"# {manifest['name']}",
        "# Selective rules: only matched services use the proxy.",
        f"# Generated from config/services.json; checked {manifest['last_checked']}.",
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
    json_dump(rules, output / "custom_routing_rules.json")


def build_index(manifest: dict, output: Path) -> None:
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
    body = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(manifest['name'])}</title>
<style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}}code{{background:#f1f3f5;padding:.15rem .3rem;border-radius:.25rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;text-align:left;vertical-align:top}}a{{margin-right:.6rem}}</style>
<h1>{html.escape(manifest['name'])}</h1>
<p>Generated {html.escape(manifest['last_checked'])}. Public, unauthenticated rule files; no node credentials or subscription tokens are included.</p>
<h2>Downloads</h2>
<ul>
<li><a href="shadowrocket/{html.escape(manifest['slug'], quote=True)}.list">Shadowrocket rule set</a></li>
<li><a href="v2rayn/custom_routing_rules.json">v2rayN custom routing JSON</a></li>
</ul>
<h2>Evidence</h2>
<table><thead><tr><th>Service</th><th>Status</th><th>Why included</th><th>Sources</th></tr></thead><tbody>{''.join(service_rows)}</tbody></table>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "public")
    args = parser.parse_args()

    manifest = load_manifest()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    slug = manifest["slug"]
    build_shadowrocket(manifest, output / "shadowrocket" / f"{slug}.list")
    build_v2rayn(manifest, output / "v2rayn")
    build_index(manifest, output / "index.html")
    (output / "availability.json").write_text(
        json.dumps(
            {
                "name": manifest["name"],
                "slug": manifest["slug"],
                "last_checked": manifest["last_checked"],
                "services": manifest["services"],
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

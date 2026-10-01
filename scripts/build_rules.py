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

DESCRIPTION_ZH = {
    "hk": "针对从香港出口不可用或受地区限制的服务进行选择性路由",
    "cn": "中国大陆域名和 IP 直连，其余流量代理",
}
SHADOWROCKET_GEOSITE_DOMAINS = {
    "geosite:google": (
        "google.com",
        "google.com.hk",
        "google.cn",
        "googleapis.com",
        "googleapis.cn",
        "gstatic.com",
        "googleusercontent.com",
        "gmail.com",
        "googlevideo.com",
    ),
}
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


def shadowrocket_config_prefix() -> list[str]:
    timestamp = dt.datetime.now(dt.timezone.utc).astimezone(
        dt.timezone(dt.timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M:%S")
    return [
        f"# Shadowrocket: {timestamp}",
        "[General]",
        "bypass-system = true",
        "skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local, captive.apple.com",
        "tun-excluded-routes = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32, 239.255.255.250/32",
        "dns-server = system",
        "fallback-dns-server = system",
        "ipv6 = true",
        "prefer-ipv6 = false",
        "dns-direct-system = false",
        "icmp-auto-reply = true",
        "always-reject-url-rewrite = false",
        "private-ip-answer = true",
        "",
        "# direct domain fail to resolve use proxy rule",
        "dns-direct-fallback-proxy = true",
        "",
        "# The fallback behavior when UDP traffic matches a policy that doesn't support the UDP relay. Possible values: DIRECT, REJECT.",
        "udp-policy-not-supported-behaviour = REJECT",
        "",
        "[Rule]",
    ]


def write_shadowrocket_config(rules: list[str], output: Path) -> None:
    lines = shadowrocket_config_prefix()
    lines.extend(rules)
    lines.extend([
        "",
        "[Host]",
        "localhost = 127.0.0.1",
        "",
        "[URL Rewrite]",
        "'^https?://(www.)?g.cn' 'https://www.google.com' 302",
        "'^https?://(www.)?google.cn' 'https://www.google.com' 302",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_shadowrocket(manifest: dict, source: Path, output: Path) -> None:
    if manifest.get("routing_mode") == "mainland_whitelist":
        build_shadowrocket_mainland_whitelist(manifest, source, output)
        return

    policy = manifest["shadowrocket_policy"]
    rules = [
        f"# {manifest.get('display_name', manifest['name'])}",
        "# Selective rules: only matched services use the proxy.",
        f"# Generated from {source.relative_to(ROOT).as_posix()}; checked {manifest['last_checked']}.",
        "# Set the policy name below to the policy/group name in Shadowrocket.",
        "",
    ]
    for service in manifest["services"]:
        rules.append(f"# {service['name']}")
        rules.extend(f"DOMAIN-SUFFIX,{domain},{policy}" for domain in service["domains"])
        rules.append("")
    rules.extend([
        "# Default direct fallback / 默认直连兜底",
        "FINAL,DIRECT",
    ])
    write_shadowrocket_config(rules, output)


def build_shadowrocket_mainland_whitelist(manifest: dict, source: Path, output: Path) -> None:
    whitelist = manifest["mainland_whitelist"]
    direct = manifest.get("shadowrocket_direct_policy", "DIRECT")
    proxy = manifest["shadowrocket_policy"]
    rules = [
        f"# {manifest.get('display_name', manifest['name'])}",
        "# v2rayN-style Mainland China Whitelist: China traffic DIRECT, everything else PROXY.",
        f"# Generated from {source.relative_to(ROOT).as_posix()}; checked {manifest['last_checked']}.",
        "# This is a whitelist profile; it intentionally ends with a proxy fallback.",
        "",
        "# Block HTTP3/QUIC",
    ]
    if whitelist.get("block_udp443"):
        rules.append("AND,((PROTOCOL,UDP),(DEST-PORT,443)),REJECT")
    rules.append("")
    rules.append("# Google")
    for domain_rule in whitelist.get("proxy_domains", []):
        domains = SHADOWROCKET_GEOSITE_DOMAINS.get(domain_rule, (domain_rule,))
        for domain in domains:
            if domain.startswith("geosite:"):
                continue
            rules.append(f"DOMAIN-SUFFIX,{domain},{proxy}")
    rules.extend([
        "",
        "# LAN",
        f"GEOIP,LAN,{direct}",
        "",
        "# China",
        f"GEOIP,CN,{direct}",
        "",
        "# Final",
        f"FINAL,{proxy}",
    ])
    write_shadowrocket_config(rules, output)


def build_v2rayn(manifest: dict, output: Path) -> None:
    if manifest.get("routing_mode") == "mainland_whitelist":
        build_v2rayn_mainland_whitelist(manifest, output)
        return

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
    rules.append(
        {
            "port": "0-65535",
            "outboundTag": manifest.get("v2rayn_direct_outbound_tag", "direct"),
            "enabled": True,
            "remarks": "Default direct / 默认直连",
        }
    )
    json_dump(rules, output)


def build_v2rayn_mainland_whitelist(manifest: dict, output: Path) -> None:
    whitelist = manifest["mainland_whitelist"]
    direct = manifest.get("v2rayn_direct_outbound_tag", "direct")
    proxy = manifest.get("v2rayn_outbound_tag", "proxy")
    block = manifest.get("v2rayn_block_outbound_tag", "block")
    direct_ip = whitelist.get("direct_ip", [])
    direct_domain = whitelist.get("direct_domain", [])
    rules = []

    if whitelist.get("block_udp443"):
        rules.append(
            {
                "remarks": "阻断udp443",
                "outboundTag": block,
                "port": "443",
                "network": "udp",
            }
        )
    proxy_domains = whitelist.get("proxy_domains", [])
    if proxy_domains:
        rules.append(
            {
                "remarks": "代理Google",
                "outboundTag": proxy,
                "domain": proxy_domains,
            }
        )

    private_ip = [item for item in direct_ip if item == "geoip:private"]
    dns_ip = [item for item in direct_ip if item not in {"geoip:private", "geoip:cn"}]
    cn_ip = [item for item in direct_ip if item == "geoip:cn"]
    private_domain = [item for item in direct_domain if item == "geosite:private"]
    dns_domain = [item for item in direct_domain if item not in {"geosite:private", "geosite:cn"}]
    cn_domain = [item for item in direct_domain if item == "geosite:cn"]

    if private_ip:
        rules.append({"remarks": "绕过局域网IP", "outboundTag": direct, "ip": private_ip})
    if private_domain:
        rules.append({"remarks": "绕过局域网域名", "outboundTag": direct, "domain": private_domain})
    if dns_ip:
        rules.append({"remarks": "绕过中国公共DNSIP", "outboundTag": direct, "ip": dns_ip})
    if dns_domain:
        rules.append({"remarks": "绕过中国公共DNS域名", "outboundTag": direct, "domain": dns_domain})
    if cn_ip:
        rules.append({"remarks": "绕过中国IP", "outboundTag": direct, "ip": cn_ip})
    if cn_domain:
        rules.append({"remarks": "绕过中国域名", "outboundTag": direct, "domain": cn_domain})
    if whitelist.get("proxy_fallback", True):
        rules.append(
            {
                "port": "0-65535",
                "outboundTag": proxy,
                "enabled": True,
                "remarks": "Default proxy fallback / 默认代理兜底",
            }
        )
    json_dump(rules, output)


def build_index(manifests: list[dict], output: Path) -> None:
    sections = []
    for manifest in manifests:
        region = manifest["region"]
        slug = html.escape(manifest["slug"], quote=True)
        description = manifest.get("description", "")
        description_zh = DESCRIPTION_ZH.get(region, description)
        section_heading = html.escape(manifest["name"])
        sections.append(
            f"""<h2>{section_heading}</h2>
<p>{html.escape(description)}</p>
<p>{html.escape(description_zh)}</p>
<ul>
<li><a href="shadowrocket/{slug}.conf">Shadowrocket config / Shadowrocket 配置</a></li>
<li><a href="v2rayn/{slug}.json">v2rayN rule set JSON / v2rayN 规则集 JSON</a></li>
</ul>
"""
        )
    body = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>routingrules</title>
<style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}}p{{margin:.7rem 0}}ul{{padding-left:1.5rem}}li{{margin:.35rem 0}}code{{background:#f1f3f5;padding:.15rem .3rem;border-radius:.25rem}}li div+div{{margin-top:.1rem;color:#333}}a{{margin-right:.6rem}}</style>
<h1><a href="https://github.com/ryanyunfanxie/routingrules">routingrules</a></h1>
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
        build_shadowrocket(manifest, source, output / "shadowrocket" / f"{slug}.conf")
        build_v2rayn(manifest, output / "v2rayn" / f"{slug}.json")
    build_index(manifests, output / "index.html")


if __name__ == "__main__":
    main()

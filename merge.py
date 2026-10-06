import urllib.request

PLUGIN_URLS = [
    # 核心去广告与净化
    "https://kelee.one/Tool/Loon/Lpx/DragonRead_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/Weixin_external_links_unlock.lpx",
    "https://kelee.one/Tool/Loon/Lpx/JDWaimai_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/JD_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/Reddit_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/Block_HTTPDNS.lpx",
    "https://kelee.one/Tool/Loon/Lpx/BlockAdvertisers.lpx",
    "https://kelee.one/Tool/Loon/Lpx/BaiduPhoto_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/RedPaper_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/WexinMiniPrograms_Remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/Weixin_Official_Accounts_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/PinDuoDuo_remove_ads.lpx",
    "https://kelee.one/Tool/Loon/Lpx/AppleWeatherEnhancer.lpx",
    "https://kelee.one/Tool/Loon/Lpx/Prevent_DNS_Leaks.lpx",
    # X (Twitter) 净化模块
    "https://kelee.one/Tool/Loon/Lpx/Twitter_remove_ads.lpx",
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Loon/3.2.0"
    )
}
sections = {"Rule": set(), "Rewrite": set(), "Hostnames": set()}
current_section = None

for url in PLUGIN_URLS:
  try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
      content = resp.read().decode("utf-8", errors="ignore")
      for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
          continue
        if line.startswith("[") and line.endswith("]"):
          tag = line[1:-1].strip()
          current_section = (
              tag if tag in ["Rule", "Rewrite", "Mitm"] else None
          )
          continue
        if current_section == "Mitm" and "hostname" in line:
          parts = line.split("=", 1)
          if len(parts) == 2:
            for h in parts[1].split(","):
              clean_h = h.strip()
              if clean_h:
                sections["Hostnames"].add(clean_h)
        elif current_section in ["Rule", "Rewrite"]:
          if "script-path" not in line:
            sections[current_section].add(line)
  except Exception as e:
    print(f"跳过源: {url} -> {e}")

with open("all_in_one.plugin", "w", encoding="utf-8") as f:
  f.write(
      "#!name = 聚合去广告纯净版\n#!desc = 含Twitter去广告与主流净化\n#!author ="
      " AutoBuild\n#!system = iOS\n\n"
  )
  for sec in ["Rule", "Rewrite"]:
    if sections[sec]:
      f.write(f"[{sec}]\n")
      for item in sorted(sections[sec]):
        f.write(f"{item}\n")
      f.write("\n")
  if sections["Hostnames"]:
    f.write("[Mitm]\n")
    f.write(f"hostname = {', '.join(sorted(sections['Hostnames']))}\n")

print("Done!")

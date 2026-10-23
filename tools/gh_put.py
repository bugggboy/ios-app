#!/usr/bin/env python3
"""通过 GitHub Contents API 写文件，绕开 git push。

本机到 GitHub 的 git 通道经常被代理掐断（CONNECT tunnel failed 502），
但 api.github.com 走 curl/urllib 是通的，所以用这个脚本兜底。

用法：
    GH_TOKEN=ghp_xxx python tools/gh_put.py <owner/repo> <branch> <本地文件> [远程路径] [-m 提交信息]

例：
    python tools/gh_put.py bugggboy/ios-app main README.md
    python tools/gh_put.py bugggboy/borealis wiliwili .github/workflows/ios.yml
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def request(method, url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "gh-put")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        return e.code, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="owner/name")
    parser.add_argument("branch")
    parser.add_argument("local_path")
    parser.add_argument("remote_path", nargs="?")
    parser.add_argument("-m", "--message", default=None)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("需要 GH_TOKEN 环境变量")

    remote = (args.remote_path or args.local_path).replace("\\", "/").lstrip("./")
    with open(args.local_path, "rb") as f:
        raw = f.read()
    content = base64.b64encode(raw).decode()
    message = args.message or f"update {remote}"

    base = f"{API}/repos/{args.repo}/contents/{remote}"
    status, existing = request("GET", f"{base}?ref={args.branch}", token)
    payload = {"message": message, "content": content, "branch": args.branch}
    if status == 200:
        payload["sha"] = existing["sha"]
        action = "更新"
    elif status == 404:
        action = "新建"
    else:
        sys.exit(f"读取远端失败 {status}: {existing}")

    status, result = request("PUT", base, token, payload)
    if status in (200, 201):
        commit = result.get("commit", {})
        print(f"{action}成功 {args.repo}:{remote} @ {args.branch}  commit={commit.get('sha', '')[:7]}")
    else:
        sys.exit(f"写入失败 {status}: {result}")


if __name__ == "__main__":
    main()

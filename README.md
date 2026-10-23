# iOS 15+ 巨魔自用应用 · 无 Mac 开发流水线

目标设备：iPhone 13 / iOS 15.x / 已装 TrollStore。应用**不签名、不上架**，只用巨魔安装。

没有 Mac 也能开发，靠的是一条分工：**Windows 上只写代码，编译和测试交给 GitHub Actions 的 macOS 机器，产物是一个未签名 IPA，手机用 TrollStore 装。**

```
Windows 改代码 ──git push──▶ GitHub Actions（macos-26）
                                  ├── xcodegen generate（现生成 .xcodeproj）
                                  ├── 单元测试 + 模拟器启动截图
                                  └── Release 编译（CODE_SIGNING_ALLOWED=NO）
                                          ↓
                                  MyApp-unsigned.ipa
                                          ↓
                             手机 Safari 下载 → 分享给 TrollStore → 安装
```

## 和 ios-ci-workflows 的关系

本地装的 `ios-ci-workflows` 技能里，**只有 Build & Test 那一半用得上**。TestFlight 那整套（Apple 开发者账号、4 项 App Store Connect 凭证、自动签名、验收 Issue）对你这种情况**全部作废** —— 未签名 + 巨魔安装不需要任何证书，也不需要 99 美元年费。

所以这个仓库没有 `.ios-ci.yml`，也没引用上游工作流，而是自己写了一份最小工作流 `ios.yml`；但保留了它的核心纪律：**CI 是唯一测试入口、改代码必须带测试、不用 `sleep` 等 UI**。

## 目录

```
project.yml                 工程定义（XcodeGen 读它生成 .xcodeproj；.xcodeproj 不进仓库）
Sources/                    应用代码
  MyApp.swift               入口
  ContentView.swift         界面（iOS 15 兼容写法）
  AppInfo.swift             纯逻辑，被单元测试覆盖
  SystemSummary.swift       机型 / 系统版本
  Assets.xcassets/          AppIcon（icon-1024.png 是脚本生成的占位图）
Tests/AppInfoTests.swift    单元测试
tools/make_icon.py          生成占位图标：python tools/make_icon.py
.github/workflows/ios.yml   测试 + 打未签名 IPA
AGENTS.md                   给 AI 的硬规则（iOS 15 限制、禁止加签名等）
```

## 一次性准备

1. 在 GitHub 建一个仓库（私有也行，注意 macOS 分钟数按 10 倍计费；公开仓库免费）。
2. 把本目录推上去：

   ```bash
   git init -b main
   git add -A
   git commit -m "初始骨架"
   git remote add origin https://github.com/<你的账号>/<仓库名>.git
   git push -u origin main
   ```

3. 打开仓库的 **Actions** 页，第一次会问是否允许运行工作流，点允许。等 `iOS · 测试 + 未签名 IPA` 跑完。
4. 跑完后在 Run 页面底部下载 `ipa-<run number>` 附件，解压得到 `MyApp-unsigned.ipa`。

不需要配任何 Secret。

## 日常循环

1. 改 `Sources/` 里的代码，同时补 `Tests/` 的测试。
2. `git push`，等 Actions 跑完（第一次约 6–8 分钟，之后有缓存约 4 分钟）。
3. 红了就看日志和 `launch.png`；绿了就下载 IPA 装机。
4. 装机后验收，有问题回第 1 步。

**没有 Mac 时，`launch.png` 是你唯一能"看见"界面的东西** —— 每次跑完都会有一张模拟器启动截图。要看别的页面，就在测试里把界面导航过去再截图，或者临时改 `ContentView` 的默认页。

## 把 IPA 送进手机（三种，按方便程度排）

**A. 同一 Wi-Fi + 本机小服务（最快，不用上传）**

```bash
# 在解压出 ipa 的目录里执行，手机浏览器打开 http://<电脑局域网IP>:8000
python -m http.server 8000
```

手机 Safari 打开那个地址 → 点 `MyApp-unsigned.ipa` → 下载 → 在「文件」里点它 → 分享 → TrollStore。

**B. GitHub Release 直链（打标签时自动生成）**

```bash
git tag v1.0.0 && git push origin v1.0.0
```

工作流会把 IPA 挂到这个 Release，手机 Safari 直接打开 Release 页面点附件即可。

**C. iCloud Drive**：电脑上传到 iCloud.com，手机「文件」里取出。

> 不要用 Actions 附件直接下载 —— 附件是 zip 套 ipa，手机解压很别扭。

## TrollStore 安装

1. 在「文件」App 里点 IPA → 右上角分享 → **TrollStore** → Install。
2. 首次安装会弹「TrollStore 将永久注册此应用」，确认即可。
3. 之后覆盖安装新版本，直接装同一个 Bundle ID 的 IPA，数据保留。

## 改名字 / 换 Bundle ID

| 改什么 | 去哪里 |
| --- | --- |
| 桌面显示名 | `project.yml` → `CFBundleDisplayName` |
| Bundle ID | `project.yml` → `PRODUCT_BUNDLE_IDENTIFIER`（同时改 `ios.yml` 的 `BUNDLE_ID`） |
| 版本号 | `project.yml` → `MARKETING_VERSION`；build 号用 run number 自动递增 |
| 图标 | 覆盖 `Sources/Assets.xcassets/AppIcon.appiconset/icon-1024.png`，或改 `tools/make_icon.py` 的 `--bg` |

## 已知边界

- **不支持**：App 内购买、推送通知、iCloud 同步、App Groups、HealthKit —— 这些依赖签名和 provisioning profile，未签名构建里拿不到。真要就得走 `ldid -S` 嵌 entitlements（巨魔会放行一部分），但复杂度会上一档，先别碰。
- **iOS 15 语言限制**：不能用 iOS 16+ 的 API（`NavigationStack`、`Charts`、`Grid`、`@Observable`、`SwiftData`、`.presentationDetents` 等）。详见 `AGENTS.md`。
- **模拟器只跑最新 iOS**：测试跑在 runner 上的 iOS 26 模拟器，部署目标仍是 15.0。真机行为差异得靠手机验收。
- **分钟数**：私有仓库 macOS 按 10 倍计费，免费额度 2000 分钟/月 ≈ 200 分钟 macOS ≈ 40 次构建。

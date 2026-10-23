# AGENTS.md

这个仓库用 **Windows 开发 + GitHub Actions 的 macOS 机器编译**，产物是未签名 IPA，装在已越狱 / 已装 TrollStore 的 iOS 15 iPhone 13 上。

改代码前先读这份，和 README 冲突时以本文件为准。

## 不可违反

- **不引入任何签名**。不要加证书、不要改 `CODE_SIGNING_ALLOWED` / `CODE_SIGNING_REQUIRED` / `CODE_SIGNING_IDENTITY`，不要在 `project.yml` 里填 `DEVELOPMENT_TEAM`。巨魔安装时自己重签。
- **部署目标保持 iOS 15.0**。不要为了"顺手"改成 16.0 或更高。
- **不用 iOS 16+ 的 API**。编译能过不等于 iOS 15 能跑 —— 用 `@available` 兜底或者干脆换个写法。
- **CI 是唯一测试入口**。本地没有 Xcode，不要声称"我在本地跑通了"。改完 push，看 Actions 结果。
- **改代码必须带测试**。纯逻辑放 `Sources/` 里可测的类型（参考 `AppInfo`），UI 层尽量薄。
- **不提交 .xcodeproj**。它由 `xcodegen generate` 现生成，改了也会被工作流覆盖。
- **密钥、证书、账号信息一律不进仓库**。

## iOS 15 兼容黑名单（写了就编译不过或运行崩）

| API | 起始版本 | 替代 |
| --- | --- | --- |
| `NavigationStack` / `.navigationDestination` | 16 | `NavigationView` + `NavigationLink` |
| `Grid` / `GridRow` | 16 | `LazyVGrid` / `HStack` |
| `Charts` 框架 | 16 | 自绘或第三方 |
| `@Observable` / Observation | 17 | `ObservableObject` + `@Published` |
| `SwiftData` | 17 | 手写文件 / SQLite / Core Data |
| `.presentationDetents` | 16 | `.sheet` 固定高度 |
| `ShareLink` | 16 | `UIActivityViewController` |
| `LabeledContent` | 16 | `HStack` + `Spacer` |
| `.scrollContentBackground(.hidden)` | 16 | `UITableView.appearance()` |
| `.fontDesign` / `.fontWidth` | 16 | 指定 `Font.system(size:design:)` |
| `Toggle` 的 `.tint` 精细控制 | 16 | 换 `Color` 或自绘 |
| `Text(...).bold()` 的 `.bold(true)` 重载 | 16 | `fontWeight(.semibold)` |

Swift 语言特性按 Swift 5 写（`SWIFT_VERSION: 5.0`），不要用 Swift 6 严格并发独有的写法。

## 产物约定

- 工作流固定产出 `MyApp-unsigned.ipa`，结构必须是 `Payload/MyApp.app/...`。
- 打包用 `/usr/bin/ditto -c -k --sequesterRsrc --keepParent`，不要用 `zip`（会丢符号链接，带 framework 时必崩）。
- 打包前工作流会检查 `_CodeSignature` 不存在、`MinimumOSVersion` 为 15.0；这两项失败要先修，不要绕过检查。

## 第三方依赖

- 优先用系统框架。需要第三方库时走 SPM，并在 `project.yml` 里声明 `packages`。
- **不要用 CocoaPods**：没有 Mac，`pod install` 在这条链路上很别扭。
- 引入的库必须支持 iOS 15（看它的 `Package.swift` 里 `platforms: [.iOS(.v15)]` 或更低）。

## 验收方式

CI 全绿只代表"写了的测试在 iOS 26 模拟器上过了"。真正验收只能在 iPhone 13 / iOS 15 真机上做：装机后看启动、看界面、看数据是否保留（覆盖安装）。界面问题优先在 `launch.png` 和测试截图里定位，别猜。

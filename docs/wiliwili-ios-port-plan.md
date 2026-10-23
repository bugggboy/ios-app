# wiliwili → iOS 14+ 移植方案（方案 C）

目标：把 [xfangfang/wiliwili](https://github.com/xfangfang/wiliwili)（GPL-3.0）真正移植到 iOS，**部署目标 14.0**（iOS 14 及以上都能装），产出未签名 `wiliwili.ipa`，用 TrollStore 安装。

维护方式：上游明确不收 iOS 补丁，所以维护自己的 fork（已建 `bugggboy/wiliwili`），定期 rebase 上游 `yoga` 分支。

## 一、勘察结论（2026-10-23）

上游事实：

- 默认分支 `yoga`，851 个文件、134 个 cpp + 131 个 hpp、仓库约 27 MB、C++ 为主、GPL-3.0
- README 原话：**"Android / iOS 不在讨论之内"**

但它依赖的 UI 库 **borealis（`xfangfang/borealis`，分支 `wiliwili`）已经具备 iOS 支持**，这是整个方案能成立的关键：

| 已有能力 | 位置 |
| --- | --- |
| `PLATFORM_IOS` 平台开关 | `library/cmake/commonOption.cmake` |
| IPA 相关参数 `IOS_CODE_SIGN_IDENTITY`、`IOS_GUI_IDENTIFIER` | 同上 |
| iOS 交叉编译工具链（leetal/ios-cmake） | `library/cmake/ios.toolchain.cmake` |
| iOS 应用外壳：`iOSBundleInfo.plist.in`、Splash.storyboard、全套 AppIcon | `demo/ios/` |
| iOS 平台实现 | `library/lib/platforms/desktop/ios_darwin.mm` |
| SDL2 后端（窗口/触摸/输入法） | `library/lib/platforms/sdl/` |
| iOS 下强制 `USE_LIBROMFS`（资源编进二进制） | `commonOption.cmake` |

wiliwili 自身情况：

- 应用代码里**没有** iOS 专用代码
- 只有两个文件出现 `PLATFORM_IOS`：`CMakeLists.txt`（链接 `CoreMedia`/`CoreText`/`VideoToolbox` 框架）、`library/CMakeLists.txt`（iOS 下关掉系统 curl、禁用 opencc）

**结论：平台层已经存在，缺的是三件事** —— 把 mpv/ffmpeg 编到 iOS、写构建胶水、补 iOS 分支代码。

## 二、里程碑

| 阶段 | 目标 | 验收 |
| --- | --- | --- |
| M0 | 工具链验证：borealis 的 `demo/ios` 在 CI 上编出 `.app` 并在模拟器启动 | Actions 出截图，证明 toolchain + GLES + SDL 全通 |
| M1 | 为 `arm64-ios` 产出 libmpv + ffmpeg 静态库（开 VideoToolbox 硬解） | demo 里播一个本地 mp4 成功 |
| M2 | wiliwili 主程序 `PLATFORM_IOS=ON` 编过并启动到首页 | 启动截图出现分区/推荐列表 |
| M3 | 功能补齐：登录、视频播放、弹幕，打包未签名 IPA | 真机 TrollStore 安装可看视频 |

## 三、iOS 14 部署目标的一个坑（必须先验证）

- Apple 官方支持页显示：**Xcode 26 / 26.6 的 iOS 部署目标范围是 15–26**。也就是说，用 Xcode 26 的 `.xcodeproj` 构建链，把 `IPHONEOS_DEPLOYMENT_TARGET` 设成 14.0 会被钳制或报错。
- 但 wiliwili 走的是 **CMake + clang 直调**（`ios.toolchain.cmake` 传 `-mios-version-min=14.0`），不经过 Xcode 的工程级校验，**很可能能真的编出 minos=14.0 的 Mach-O**。
- 这条必须在 M0 就用实测结论定下来：编完读 Mach-O 的 `LC_BUILD_VERSION`，看 `minos` 是不是 14.0。
  - 若成立 → 目标 14.0，一套工具链搞定。
  - 若不成立 → 两条退路：① CI 换 `macos-14` + Xcode 15.x（支持 iOS 12+ 部署目标，但老 runner 可能已下线）；② 接受 15.0。

## 四、已知风险点

1. **mpv 的 iOS 构建**是最大不确定项：需要交叉编译 libass / fontconfig / freetype / harfbuzz，或者改用 MPVKit 的 xcframework。M1 就是在赌这个，赌不赢 M2/M3 都无从谈起。
2. OpenGL ES 在 iOS 已标记废弃，但 iOS 15 仍可用；nanovg 走 GLES2 后端。
3. iOS 沙盒路径：缓存、资源、配置文件的位置全部要改；资源已被 libromfs 接管。
4. 未签名：`IOS_CODE_SIGN_IDENTITY` 留空，产出 `.app` 后手工组 `Payload/` 再用 `ditto` 打包，与本仓库 iOS 流水线一致。
5. 迭代成本：每次 CI 约 8 分钟，移植期预计 30–60 次构建。

## 四、为什么不选更省事的路

- SwiftUI 复刻能还原交互，但等于重写一个客户端，且永远追不上上游功能更新。
- 网页壳最省事，但拿不到 wiliwili 的原生手感与弹幕层。

既然目标就是"和 wiliwili 一模一样"，只有真移植能满足。

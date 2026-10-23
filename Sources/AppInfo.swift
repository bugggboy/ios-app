import Foundation

/// 只做纯逻辑、不碰 UIKit —— 这一层才能在 CI 里被廉价的单元测试覆盖。
struct AppInfo: Equatable {
    let name: String
    let version: String
    let build: String

    init(name: String, version: String, build: String) {
        self.name = name
        self.version = version
        self.build = build
    }

    init(infoDictionary info: [String: Any]) {
        let displayName = info["CFBundleDisplayName"] as? String
        let bundleName = info["CFBundleName"] as? String
        self.name = displayName ?? bundleName ?? "MyApp"
        self.version = info["CFBundleShortVersionString"] as? String ?? "0.0"
        self.build = info["CFBundleVersion"] as? String ?? "0"
    }

    static func current(bundle: Bundle = .main) -> AppInfo {
        AppInfo(infoDictionary: bundle.infoDictionary ?? [:])
    }

    var displayVersion: String {
        "v\(version) (\(build))"
    }
}

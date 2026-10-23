import XCTest
@testable import MyApp

final class AppInfoTests: XCTestCase {

    func testDisplayVersionIncludesBuild() {
        let info = AppInfo(name: "MyApp", version: "1.2", build: "7")
        XCTAssertEqual(info.displayVersion, "v1.2 (7)")
    }

    func testPrefersDisplayName() {
        let info = AppInfo(infoDictionary: [
            "CFBundleDisplayName": "我的应用",
            "CFBundleName": "MyApp"
        ])
        XCTAssertEqual(info.name, "我的应用")
    }

    func testFallsBackWhenKeysMissing() {
        let info = AppInfo(infoDictionary: [:])
        XCTAssertEqual(info.name, "MyApp")
        XCTAssertEqual(info.version, "0.0")
        XCTAssertEqual(info.build, "0")
    }

    func testCurrentReadsBundleVersion() {
        let info = AppInfo.current()
        XCTAssertFalse(info.version.isEmpty)
        XCTAssertNotEqual(info.version, "0.0", "Info.plist 里应该带上 MARKETING_VERSION")
    }
}

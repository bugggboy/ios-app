import UIKit

struct SystemSummary {
    let osVersion: String
    let model: String
    let machine: String

    static func current() -> SystemSummary {
        let device = UIDevice.current
        return SystemSummary(
            osVersion: device.systemVersion,
            model: device.model,
            machine: Hardware.machineIdentifier
        )
    }
}

/// 取 "iPhone14,2" 这种机型标识，排查机型相关问题时会用到。
enum Hardware {
    static var machineIdentifier: String {
        var info = utsname()
        uname(&info)
        let mirror = Mirror(reflecting: info.machine)
        return mirror.children.reduce(into: "") { result, element in
            guard let value = element.value as? Int8, value != 0 else { return }
            result.append(Character(UnicodeScalar(UInt8(bitPattern: value))))
        }
    }
}

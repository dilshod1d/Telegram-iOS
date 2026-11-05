import Foundation
import UrlEscaping

public enum LocalLinkRisk: Equatable {
    case login
    case direction
    case mixed
}

/// Local structural signals, not a malware or reputation verdict.
public func localLinkRisk(_ value: String) -> LocalLinkRisk? {
    guard let url = canonicalExternalUrl(from: value), let scheme = url.scheme?.lowercased(), scheme == "http" || scheme == "https" else {
        return nil
    }
    if url.user != nil || url.password != nil {
        return .login
    }
    let decoded = value.removingPercentEncoding ?? value
    if decoded.unicodeScalars.contains(where: { (0x202a...0x202e).contains($0.value) || (0x2066...0x2069).contains($0.value) }) {
        return .direction
    }
    let encodedHost = url.host?.lowercased() ?? ""
    let host = encodedHost.idnaDecoded ?? encodedHost
    for label in host.split(separator: ".") {
        let scripts = ["\\p{Latin}", "\\p{Cyrillic}", "\\p{Greek}"]
        if scripts.filter({ label.range(of: $0, options: .regularExpression) != nil }).count > 1 {
            return .mixed
        }
    }
    return nil
}

/// APK metadata is checked before previewing or exporting; content is never uploaded.
public func isApkFile(name: String?, mimeType: String) -> Bool {
    return name?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased().hasSuffix(".apk") == true
        || mimeType.split(separator: ";").first?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == "application/vnd.android.package-archive"
}

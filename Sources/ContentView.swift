import SwiftUI

struct ContentView: View {
    private let app = AppInfo.current()
    private let system = SystemSummary.current()

    var body: some View {
        NavigationView {
            List {
                Section(header: Text("应用")) {
                    row("名称", app.name)
                    row("版本", app.displayVersion)
                }
                Section(header: Text("设备")) {
                    row("机型", system.machine)
                    row("系统", "iOS " + system.osVersion)
                }
                Section(header: Text("下一步")) {
                    Text("改 Sources/ContentView.swift 就是改这个界面，push 之后 CI 会重新出包。")
                        .font(.footnote)
                        .foregroundColor(.secondary)
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle(app.name)
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    private func row(_ title: String, _ value: String) -> some View {
        HStack {
            Text(title)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

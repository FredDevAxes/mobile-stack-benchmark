import Combine

@MainActor final class Progress: ObservableObject {
    @Published var value = 0.0
    var time: Double { value }
    func move(to target: Double, reduced: Bool, done: @escaping () -> Void) {
        value = target
        done()
    }
}

import Combine
import UIKit

@MainActor final class Progress: NSObject, ObservableObject {
    @Published var time = 0.0
    var value: Double {
        var lo = 0.0
        var hi = 1.0
        for _ in 0..<24 {
            let t = (lo + hi) / 2
            let x = 3 * (1 - t) * (1 - t) * t * 0.4 + 3 * (1 - t) * t * t * 0.2 + t * t * t
            if x < time { lo = t } else { hi = t }
        }
        let t = (lo + hi) / 2
        return 3 * (1 - t) * t * t + t * t * t
    }
    private var link: CADisplayLink?
    private var start = 0.0, from = 0.0, target = 0.0
    private var done: (() -> Void)?
    func move(to target: Double, reduced: Bool, done: @escaping () -> Void) {
        link?.invalidate()
        if reduced {
            time = target
            done()
            return
        }
        self.target = target
        self.from = time
        self.start = CACurrentMediaTime()
        self.done = done
        let next = CADisplayLink(target: self, selector: #selector(tick))
        link = next
        next.add(to: .main, forMode: .common)
    }
    @objc private func tick() {
        let elapsed = min(1, (CACurrentMediaTime() - start) / 0.4)
        time = from + (target - from) * elapsed
        if elapsed == 1 {
            link?.invalidate()
            link = nil
            let completion = done
            done = nil
            completion?()
        }
    }
}

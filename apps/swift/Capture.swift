#if CAPTURE
    func captureCurve(_ time: Double) -> Double {
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
#endif

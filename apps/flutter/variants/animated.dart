import 'package:flutter/widgets.dart';

class Progress extends ChangeNotifier {
  late final AnimationController clock;
  Progress({required TickerProvider vsync}) {
    clock = AnimationController(
      vsync: vsync,
      duration: const Duration(milliseconds: 400),
    )..addListener(notifyListeners);
  }
  double get time => clock.value;
  double get value => const Cubic(0.4, 0, 0.2, 1).transform(clock.value);
  Future<void> move(double target, bool reduced) async {
    if (reduced) {
      clock.value = target;
      return;
    }
    if (target == 1) {
      await clock.forward();
    } else {
      await clock.reverse();
    }
  }

  @override
  void dispose() {
    clock.dispose();
    super.dispose();
  }
}

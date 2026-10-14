import 'package:flutter/widgets.dart';

class Progress extends ChangeNotifier {
  Progress({TickerProvider? vsync});
  double value = 0;
  double get time => value;
  Future<void> move(double target, bool reduced) async {
    value = target;
    notifyListeners();
  }
}

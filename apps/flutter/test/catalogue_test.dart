import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_stack_benchmark/main.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile_stack_benchmark/catalogue.dart';

void main() {
  final products = (jsonDecode(
    File('assets/products.json').readAsStringSync(),
  ) as List).map((j) => Product(j)).toList();
  testWidgets('iOS Reduce Motion skips the custom transition', (tester) async {
    SharedPreferences.setMockInitialValues({});
    tester.platformDispatcher.accessibilityFeaturesTestValue =
        const FakeAccessibilityFeatures(reduceMotion: true);
    addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(const MaterialApp(home: Catalogue()));
    await tester.pumpAndSettle();
    await tester.tap(find.bySemanticsLabel('Open p001'));
    await tester.pump();
    final dynamic state = tester.state(find.byType(Catalogue));
    expect(state.busy, false);
    expect(find.text(products.first.description), findsOneWidget);
    tester.platformDispatcher.accessibilityFeaturesTestValue =
        const FakeAccessibilityFeatures();
    await tester.pump();
    expect(state.reducedMotion, false);
  });
  test('fixed data and case insensitive explicit search', () {
    expect(products.length, 200);
    expect(filtered(products, 'TRAIL PACK', false, {}).length, 10);
    expect(filtered(products, 'unknown', false, {}), isEmpty);
    expect(filtered(products, '', false, {}), products);
  });
  test('favorites combine with search and preserve order', () {
    expect(
      filtered(products, 'pack', true, {'p021', 'p001'}).map((p) => p.id),
      ['p001', 'p021'],
    );
    expect(products.first.price, '€15.00');
  });
}

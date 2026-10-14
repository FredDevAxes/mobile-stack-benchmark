import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_stack_benchmark/catalogue.dart';

void main() {
  final products = (jsonDecode(
    File('assets/products.json').readAsStringSync(),
  ) as List).map((j) => Product(j)).toList();
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

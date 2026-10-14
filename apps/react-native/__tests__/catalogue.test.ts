import { filtered, products, toggled, price } from '../src/catalogue';
test('fixed dataset and explicit substring search', () => {
  expect(products).toHaveLength(200);
  expect(filtered('TRAIL PACK', false, [])).toHaveLength(10);
  expect(filtered('unknown', false, [])).toHaveLength(0);
  expect(filtered('', false, [])).toEqual(products);
});
test('favorites combine with search and preserve order', () => {
  expect(filtered('pack', true, ['p021', 'p001']).map(p => p.id)).toEqual([
    'p001',
    'p021',
  ]);
  expect(toggled(['p001'], 'p001')).toEqual([]);
  expect(toggled([], 'p001')).toEqual(['p001']);
  expect(price(1500)).toBe('€15.00');
});

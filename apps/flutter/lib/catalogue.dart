class Product {
  final String id, name, category, description, imageKey;
  final int priceCents;
  Product(Map<String, dynamic> json)
    : id = json['id'],
      name = json['name'],
      category = json['category'],
      description = json['description'],
      imageKey = json['imageKey'],
      priceCents = json['priceCents'];
  String get price => '€${(priceCents / 100).toStringAsFixed(2)}';
}

List<Product> filtered(
  List<Product> products,
  String query,
  bool only,
  Set<String> favorites,
) => products
    .where(
      (p) =>
          p.name.toLowerCase().contains(query.toLowerCase()) &&
          (!only || favorites.contains(p.id)),
    )
    .toList();

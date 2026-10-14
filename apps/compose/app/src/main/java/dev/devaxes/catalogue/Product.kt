package dev.devaxes.catalogue

data class Product(
    val id: String,
    val name: String,
    val category: String,
    val priceCents: Int,
    val description: String,
    val imageKey: String,
) {
    val price: String get() = "€%.2f".format(java.util.Locale.US, priceCents / 100.0)
}

fun filtered(
    products: List<Product>,
    query: String,
    only: Boolean,
    favorites: Set<String>,
): List<Product> = products.filter { it.name.contains(query, ignoreCase = true) && (!only || it.id in favorites) }

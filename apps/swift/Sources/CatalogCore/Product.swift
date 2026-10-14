import Foundation

public struct Product: Codable, Identifiable, Equatable, Sendable {
    public let id: String
    public let name: String
    public let category: String
    public let priceCents: Int
    public let description: String
    public let imageKey: String
    public var price: String { String(format: "€%.2f", Double(priceCents) / 100) }
}
public func filtered(_ products: [Product], query: String, only: Bool, favorites: Set<String>)
    -> [Product]
{
    products.filter {
        $0.name.lowercased().contains(query.lowercased()) && (!only || favorites.contains($0.id))
    }
}

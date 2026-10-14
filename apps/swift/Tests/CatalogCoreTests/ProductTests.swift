import XCTest

@testable import CatalogCore

final class ProductTests: XCTestCase {
    func testSearchAndFavoriteComposition() throws {
        let data = Data(
            """
            [{"id":"p001","name":"Trail pack 01","category":"Carry","priceCents":1500,"description":"sample","imageKey":"gear-01"},
            {"id":"p021","name":"Trail pack 02","category":"Carry","priceCents":1600,"description":"sample","imageKey":"gear-01"}]
            """.utf8)
        let products = try JSONDecoder().decode([Product].self, from: data)
        XCTAssertEqual(filtered(products, query: "TRAIL", only: false, favorites: []), products)
        XCTAssertTrue(filtered(products, query: "unknown", only: false, favorites: []).isEmpty)
        XCTAssertEqual(
            filtered(products, query: "pack", only: true, favorites: ["p001"]), [products[0]])
        XCTAssertEqual(products[0].price, "€15.00")
    }
}

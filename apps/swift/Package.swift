// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "CatalogCore",
    products: [.library(name: "CatalogCore", targets: ["CatalogCore"])],
    targets: [
        .target(name: "CatalogCore"),
        .testTarget(name: "CatalogCoreTests", dependencies: ["CatalogCore"]),
    ]
)

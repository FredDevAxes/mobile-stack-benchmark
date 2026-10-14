import SwiftUI

@main struct CatalogueApp: App {
    var body: some Scene { WindowGroup { Catalogue() }.defaultSize(width: 390, height: 844) }
}
private struct ImagePositions: PreferenceKey {
    static let defaultValue: [String: CGRect] = [:]
    static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue(), uniquingKeysWith: { _, new in new })
    }
}
struct Catalogue: View {
    let products: [Product]
    @State private var favorites: Set<String>
    @State private var draft = ""
    @State private var query = ""
    @State private var only = false
    @State private var selected: Product?
    @State private var source = CGRect.zero
    @State private var positions: [String: CGRect] = [:]
    @State private var busy = false
    @State private var queued = false
    @State private var closing = false
    @StateObject private var progress = Progress()
    @Environment(\.accessibilityReduceMotion) private var reduced
    init() {
        let url = Bundle.main.url(forResource: "products", withExtension: "json")!
        products = try! JSONDecoder().decode([Product].self, from: Data(contentsOf: url))
        _favorites = State(
            initialValue: Set(UserDefaults.standard.stringArray(forKey: "favorites") ?? [])
                .intersection(products.map(\.id)))
    }
    private var visible: [Product] {
        filtered(products, query: query, only: only, favorites: favorites)
    }
    private func toggle(_ p: Product) {
        guard !busy else { return }
        if favorites.contains(p.id) { favorites.remove(p.id) } else { favorites.insert(p.id) }
        UserDefaults.standard.set(Array(favorites), forKey: "favorites")
    }
    private func open(_ p: Product) {
        guard !busy, selected == nil, let rect = positions[p.id] else { return }
        source = rect
        selected = p
        busy = true
        progress.move(to: 1, reduced: reduced) {
            busy = false
            if queued {
                queued = false
                close()
            }
        }
    }
    private func close() {
        if busy {
            if !closing { queued = true }
            return
        }
        busy = true
        closing = true
        progress.move(to: 0, reduced: reduced) {
            selected = nil
            busy = false
            closing = false
        }
    }
    private func action(_ title: String, id: String? = nil, _ body: @escaping () -> Void)
        -> some View
    {
        Button(title, action: body).font(.system(size: 16)).foregroundStyle(
            Color(red: 0.137, green: 0.353, blue: 0.271)
        ).accessibilityLabel(id ?? title).accessibilityIdentifier(id ?? title)
    }
    private func photo(_ p: Product, width: CGFloat, height: CGFloat, radius: CGFloat) -> some View
    {
        let path = Bundle.main.url(
            forResource: p.imageKey, withExtension: "png", subdirectory: "images")!.path
        return Image(uiImage: UIImage(contentsOfFile: path)!).resizable().scaledToFill().frame(
            width: width, height: height
        ).clipped().clipShape(RoundedRectangle(cornerRadius: radius)).accessibilityHidden(true)
    }
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .topLeading) {
                VStack(spacing: 0) {
                    Text("Trail catalogue").font(.system(size: 20, weight: .semibold)).frame(
                        maxWidth: .infinity, alignment: .leading
                    ).padding(.horizontal, 16).frame(height: 52)
                    HStack(spacing: 8) {
                        TextField("Search products", text: $draft).font(.system(size: 16)).padding(
                            .horizontal, 10
                        ).frame(height: 44).overlay(RoundedRectangle(cornerRadius: 8).stroke(.gray))
                            .accessibilityIdentifier("Search products")
                        action("Search") { query = draft }
                    }.padding(.horizontal, 16).frame(height: 44)
                    HStack {
                        action("\(only ? "☑" : "☐") Favorites only", id: "Favorites only") {
                            only.toggle()
                        }
                        Spacer()
                        action("Clear filters") {
                            draft = ""
                            query = ""
                            only = false
                        }
                    }.padding(.horizontal, 16).frame(height: 40)
                    if visible.isEmpty { Text("No products found").padding(32) }
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(visible) { p in
                                VStack(spacing: 0) {
                                    Button {
                                        open(p)
                                    } label: {
                                        photo(
                                            p, width: geometry.size.width - 32, height: 180,
                                            radius: 16
                                        ).opacity(selected?.id == p.id ? 0 : 1)
                                    }.accessibilityLabel("Open \(p.id)").accessibilityIdentifier(
                                        "Open \(p.id)"
                                    )
                                    .background(
                                        GeometryReader { image in
                                            Color.clear.preference(
                                                key: ImagePositions.self,
                                                value: [p.id: image.frame(in: .named("catalogue"))])
                                        })
                                    HStack {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(p.name).font(.system(size: 18))
                                            Text("\(p.category) · \(p.price)").font(
                                                .system(size: 14)
                                            ).foregroundStyle(.secondary)
                                        }
                                        Spacer()
                                        action(
                                            favorites.contains(p.id) ? "★" : "☆",
                                            id: "Favorite \(p.id)"
                                        ) { toggle(p) }.padding(12)
                                    }.frame(height: 72)
                                }
                            }
                        }.padding(.horizontal, 16).padding(.bottom, 16)
                    }
                }.disabled(selected != nil).accessibilityHidden(selected != nil)
                if let p = selected {
                    let exists = visible.contains { $0.id == p.id }
                    let t = progress.value
                    let x = exists ? source.minX * (1 - t) : 0
                    let y = exists ? source.minY + (52 - source.minY) * t : 52
                    let w =
                        exists
                        ? source.width + (geometry.size.width - source.width) * t
                        : geometry.size.width
                    let h = exists ? source.height + (280 - source.height) * t : 280
                    Color.white.opacity(t)
                    photo(p, width: w, height: h, radius: exists ? 16 * (1 - t) : 0).offset(
                        x: x, y: y
                    ).opacity(exists ? 1 : t)
                    VStack(alignment: .leading, spacing: 0) {
                        action("‹ Back", id: "Back", close).padding(.horizontal, 16).frame(
                            height: 52)
                        Color.clear.frame(height: 280)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(p.name).font(.system(size: 24))
                            Text("\(p.category) · \(p.price)").font(.system(size: 14))
                                .foregroundStyle(.secondary)
                            Text(p.description).font(.system(size: 16)).padding(.vertical, 16)
                            action(
                                favorites.contains(p.id) ? "Remove favorite" : "Add favorite",
                                id: "Favorite \(p.id)"
                            ) { toggle(p) }
                        }.padding(16)
                    }.opacity(max(0, (progress.time - 0.35) / 0.65))
                }
            }.coordinateSpace(name: "catalogue").onPreferenceChange(ImagePositions.self) {
                positions = $0
            }.background(.white)
        }.preferredColorScheme(.light)
    }
}

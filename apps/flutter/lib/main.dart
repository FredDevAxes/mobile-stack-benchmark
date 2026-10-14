import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'catalogue.dart';
import 'transition.dart';

void main() {
  runApp(
    const MaterialApp(debugShowCheckedModeBanner: false, home: Catalogue()),
  );
}

class Catalogue extends StatefulWidget {
  const Catalogue({super.key});
  @override
  State<Catalogue> createState() => _CatalogueState();
}

class _CatalogueState extends State<Catalogue>
    with SingleTickerProviderStateMixin {
  // CAPTURE_BEGIN
  double captureTime = -1;
  // CAPTURE_END
  List<Product> products = [];
  Set<String> favorites = {};
  String query = '', error = '';
  bool only = false,
      ready = false,
      busy = false,
      queued = false,
      closing = false;
  final draft = TextEditingController();
  final scroll = ScrollController();
  final rootKey = GlobalKey();
  final imageKeys = <String, GlobalKey>{};
  Product? selected;
  Rect source = Rect.zero;
  late final Progress progress;
  SharedPreferences? preferences;
  Future<void> writes = Future.value();
  @override
  void initState() {
    super.initState();
    progress = Progress(vsync: this)
      ..addListener(() {
        if (mounted) {
          setState(() {});
        }
      });
    load();
  }

  Future<void> load() async {
    final raw = await rootBundle.loadString('assets/products.json');
    final loaded = (jsonDecode(raw) as List).map((j) => Product(j)).toList();
    try {
      preferences = await SharedPreferences.getInstance();
      favorites = (preferences!.getStringList('favorites') ?? [])
          .where((id) => loaded.any((p) => p.id == id))
          .toSet();
    } catch (_) {
      error = 'Could not load favorites';
    }
    if (mounted) {
      setState(() {
        products = loaded;
        ready = true;
      });
    }
  }

  void toggle(String id) {
    if (!ready || busy) {
      return;
    }
    setState(() {
      if (!favorites.remove(id)) {
        favorites.add(id);
      }
    });
    final ids = favorites.toList();
    writes = writes.then((_) async {
      if (preferences == null ||
          !await preferences!.setStringList('favorites', ids)) {
        if (mounted) {
          setState(() {
            error = 'Could not save favorites';
          });
        }
      }
    });
  }

  Future<void> open(Product p) async {
    if (busy || selected != null) {
      return;
    }
    final image =
        imageKeys[p.id]?.currentContext?.findRenderObject() as RenderBox?;
    final root = rootKey.currentContext?.findRenderObject() as RenderBox?;
    if (image == null || root == null) {
      return;
    }
    source = image.localToGlobal(Offset.zero, ancestor: root) & image.size;
    setState(() {
      selected = p;
      busy = true;
    });
    await progress.move(1, MediaQuery.disableAnimationsOf(context));
    if (!mounted) {
      return;
    }
    setState(() {
      busy = false;
    });
    if (queued) {
      queued = false;
      close();
    }
  }

  Future<void> close() async {
    if (busy) {
      if (!closing) {
        queued = true;
      }
      return;
    }
    setState(() {
      busy = true;
      closing = true;
    });
    await progress.move(0, MediaQuery.disableAnimationsOf(context));
    if (mounted) {
      setState(() {
        selected = null;
        busy = false;
        closing = false;
      });
    }
  }

  @override
  void dispose() {
    progress.dispose();
    draft.dispose();
    scroll.dispose();
    super.dispose();
  }

  Widget button(String label, VoidCallback action, {String? semantics}) =>
      Semantics(
        label: semantics,
        button: true,
        excludeSemantics: semantics != null,
        child: TextButton(
          onPressed: action,
          style: TextButton.styleFrom(foregroundColor: const Color(0xff235a45)),
          child: Text(label, style: const TextStyle(fontSize: 16)),
        ),
      );
  Widget photo(Product p, {double radius = 16}) => ClipRRect(
    borderRadius: BorderRadius.circular(radius),
    child: Image.asset(
      'assets/images/${p.imageKey}.png',
      fit: BoxFit.cover,
      width: double.infinity,
      height: double.infinity,
    ),
  );
  @override
  Widget build(BuildContext context) {
    final data = filtered(products, query, only, favorites);
    final p = selected;
    var visualProgress = progress.value;
    var visualTime = progress.time;
    // CAPTURE_BEGIN
    if (captureTime >= 0) {
      visualProgress = const Cubic(0.4, 0, 0.2, 1).transform(captureTime);
      visualTime = captureTime;
    }
    // CAPTURE_END

    final exists = p == null || data.any((item) => item.id == p.id);
    return PopScope(
      canPop: p == null,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop && p != null) {
          close();
        }
      },
      child: Scaffold(
        backgroundColor: Colors.white,
        body: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final destination = Rect.fromLTWH(
                0,
                52,
                constraints.maxWidth,
                280,
              );
              final rect = exists
                  ? Rect.lerp(source, destination, visualProgress)!
                  : destination;
              return Stack(
                key: rootKey,
                children: [
                  ExcludeSemantics(
                    excluding: p != null,
                    child: IgnorePointer(
                      ignoring: p != null,
                      child: Column(
                        children: [
                          const SizedBox(
                            height: 52,
                            child: Align(
                              alignment: Alignment.centerLeft,
                              child: Padding(
                                padding: EdgeInsets.symmetric(horizontal: 16),
                                child: Text(
                                  'Trail catalogue',
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          SizedBox(
                            height: 44,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Semantics(
                                      identifier: "search-products",
                                      label: "Search products",
                                      child: TextField(
                                        controller: draft,
                                        autocorrect: false,
                                        enableSuggestions: false,
                                        decoration: const InputDecoration(
                                          hintText: 'Search products',
                                          border: OutlineInputBorder(),
                                          contentPadding: EdgeInsets.symmetric(
                                            horizontal: 10,
                                            vertical: 0,
                                          ),
                                        ),
                                        style: const TextStyle(fontSize: 16),
                                      ),
                                    ),
                                  ),
                                  button(
                                    'Search',
                                    () => setState(() {
                                      query = draft.text;
                                      FocusScope.of(context).unfocus();
                                    }),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          SizedBox(
                            height: 40,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Semantics(
                                    label: 'Favorites only',
                                    checked: only,
                                    child: GestureDetector(
                                      onTap: () => setState(() {
                                        only = !only;
                                      }),
                                      child: Text(
                                        '${only ? '☑' : '☐'} Favorites only',
                                      ),
                                    ),
                                  ),
                                  button(
                                    'Clear filters',
                                    () => setState(() {
                                      draft.clear();
                                      query = '';
                                      only = false;
                                    }),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          if (error.isNotEmpty) Text(error),
                          Expanded(
                            child: data.isEmpty
                                ? const Center(child: Text('No products found'))
                                : ListView.builder(
                                    controller: scroll,
                                    padding: EdgeInsets.zero,
                                    itemCount: data.length,
                                    itemBuilder: (context, index) {
                                      final item = data[index];
                                      final key = imageKeys.putIfAbsent(
                                        item.id,
                                        GlobalKey.new,
                                      );
                                      return Padding(
                                        padding: const EdgeInsets.fromLTRB(
                                          16,
                                          0,
                                          16,
                                          16,
                                        ),
                                        child: Column(
                                          children: [
                                            Semantics(
                                              label: 'Open ${item.id}',
                                              button: true,
                                              excludeSemantics: true,
                                              child: GestureDetector(
                                                onTap: () => open(item),
                                                child: SizedBox(
                                                  key: key,
                                                  height: 180,
                                                  width: double.infinity,
                                                  child: Opacity(
                                                    opacity: p?.id == item.id
                                                        ? 0
                                                        : 1,
                                                    child: photo(item),
                                                  ),
                                                ),
                                              ),
                                            ),
                                            SizedBox(
                                              height: 72,
                                              child: Row(
                                                children: [
                                                  Expanded(
                                                    child: GestureDetector(
                                                      onTap: () => open(item),
                                                      child: Column(
                                                        crossAxisAlignment:
                                                            CrossAxisAlignment
                                                                .start,
                                                        mainAxisAlignment:
                                                            MainAxisAlignment
                                                                .center,
                                                        children: [
                                                          Text(
                                                            item.name,
                                                            style:
                                                                const TextStyle(
                                                                  fontSize: 18,
                                                                ),
                                                          ),
                                                          Text(
                                                            '${item.category} · ${item.price}',
                                                            style:
                                                                const TextStyle(
                                                                  fontSize: 14,
                                                                  color: Color(
                                                                    0xff47564d,
                                                                  ),
                                                                ),
                                                          ),
                                                        ],
                                                      ),
                                                    ),
                                                  ),
                                                  button(
                                                    favorites.contains(item.id)
                                                        ? '★'
                                                        : '☆',
                                                    () => toggle(item.id),
                                                    semantics:
                                                        'Favorite ${item.id}',
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                    },
                                  ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  if (p != null) ...[
                    Positioned.fill(
                      child: ColoredBox(
                        color: Colors.white.withValues(alpha: visualProgress),
                      ),
                    ),
                    Positioned.fromRect(
                      rect: rect,
                      child: Opacity(
                        opacity: exists ? 1 : visualProgress,
                        child: photo(
                          p,
                          radius: exists ? 16 * (1 - visualProgress) : 0,
                        ),
                      ),
                    ),
                    Opacity(
                      opacity: ((visualTime - 0.35) / 0.65).clamp(0, 1),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          SizedBox(
                            height: 52,
                            child: button('‹ Back', close, semantics: 'Back'),
                          ),
                          const SizedBox(height: 280),
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  p.name,
                                  style: const TextStyle(fontSize: 24),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '${p.category} · ${p.price}',
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: Color(0xff47564d),
                                  ),
                                ),
                                Padding(
                                  padding: const EdgeInsets.symmetric(
                                    vertical: 16,
                                  ),
                                  child: Text(
                                    p.description,
                                    style: const TextStyle(fontSize: 16),
                                  ),
                                ),
                                button(
                                  favorites.contains(p.id)
                                      ? 'Remove favorite'
                                      : 'Add favorite',
                                  () => toggle(p.id),
                                  semantics: 'Favorite ${p.id}',
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  // CAPTURE_BEGIN
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: Container(
                      height: 40,
                      color: Colors.white,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [0.0, 0.25, 0.5, 0.75, 1.0]
                            .map(
                              (t) => button(
                                '${(t * 100).round()}%',
                                () => setState(() {
                                  captureTime = t;
                                }),
                                semantics: 'Capture ${(t * 100).round()}',
                              ),
                            )
                            .toList(),
                      ),
                    ),
                  ),
                  // CAPTURE_END
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

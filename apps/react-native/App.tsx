import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  AccessibilityInfo,
  Keyboard,
  BackHandler,
  FlatList,
  Image,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Product, filtered, price, products, toggled } from './src/catalogue';
import { images } from './src/images';
import { useProgress } from './src/transition';
// CAPTURE_BEGIN
import { Easing } from 'react-native';
// CAPTURE_END
type Rect = { x: number; y: number; width: number; height: number };
function Catalogue() {
  // CAPTURE_BEGIN
  const [captureTime, setCaptureTime] = useState(-1);
  // CAPTURE_END
  const [draft, setDraft] = useState('');
  const [query, setQuery] = useState('');
  const [only, setOnly] = useState(false);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Product | null>(null);
  const [source, setSource] = useState<Rect>({
    x: 16,
    y: 136,
    width: 0,
    height: 180,
  });
  const [width, setWidth] = useState(0);
  const [target, setTarget] = useState(0);
  const [reduced, setReduced] = useState(false);
  const busy = useRef(false);
  const queued = useRef(false);
  const closing = useRef(false);
  const origin = useRef({ x: 0, y: 0 });
  const root = useRef<View>(null);
  const imageRefs = useRef<Record<string, View | null>>({});
  const write = useRef(Promise.resolve());
  useEffect(() => {
    AsyncStorage.getItem('favorites')
      .then(raw => {
        if (raw) {
          const ids: unknown = JSON.parse(raw);
          if (Array.isArray(ids)) {
            setFavorites(
              ids.filter(
                (id): id is string =>
                  typeof id === 'string' && products.some(p => p.id === id),
              ),
            );
          }
        }
      })
      .catch(() => setError('Could not load favorites'))
      .finally(() => setReady(true));
    AccessibilityInfo.isReduceMotionEnabled().then(setReduced);
    const sub = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      setReduced,
    );
    return () => sub.remove();
  }, []);
  const complete = useCallback((value: number) => {
    busy.current = false;
    if (value === 0 && closing.current) {
      setSelected(null);
      closing.current = false;
    }
    if (value === 1 && queued.current) {
      queued.current = false;
      busy.current = true;
      closing.current = true;
      setTarget(0);
    }
  }, []);
  let [progress, time] = useProgress(target, reduced, complete);
  // CAPTURE_BEGIN
  if (captureTime >= 0) {
    progress = Easing.bezier(0.4, 0, 0.2, 1)(captureTime);
    time = captureTime;
  }
  // CAPTURE_END
  const close = useCallback(() => {
    if (busy.current) {
      if (!closing.current) {
        queued.current = true;
      }
      return;
    }
    busy.current = true;
    closing.current = true;
    setTarget(0);
  }, []);
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (!selected) {
        return false;
      }
      close();
      return true;
    });
    return () => sub.remove();
  }, [selected, close]);
  const toggle = (id: string) => {
    if (!ready || busy.current) {
      return;
    }
    const next = toggled(favorites, id);
    setFavorites(next);
    write.current = write.current
      .then(() => AsyncStorage.setItem('favorites', JSON.stringify(next)))
      .catch(() => setError('Could not save favorites'));
  };
  const open = (product: Product) => {
    if (busy.current || selected) {
      return;
    }
    busy.current = true;
    imageRefs.current[product.id]?.measureInWindow((x, y, w, h) => {
      setSource({
        x: x - origin.current.x,
        y: y - origin.current.y,
        width: w,
        height: h,
      });
      setSelected(product);
      setTarget(1);
    });
  };
  const data = filtered(query, only, favorites);
  const sourceExists = selected ? data.some(p => p.id === selected.id) : true;
  const mix = (a: number, b: number) => a + (b - a) * progress;
  const star = (p: Product) => (
    <Pressable
      accessibilityLabel={`Favorite ${p.id}`}
      accessibilityRole="button"
      accessibilityState={{
        selected: favorites.includes(p.id),
        disabled: !ready,
      }}
      onPress={() => toggle(p.id)}
      style={s.favorite}
    >
      <Text style={s.button}>{favorites.includes(p.id) ? '★' : '☆'}</Text>
    </Pressable>
  );
  return (
    <SafeAreaView style={s.safe}>
      <View
        ref={root}
        collapsable={false}
        style={s.root}
        onLayout={e => {
          setWidth(e.nativeEvent.layout.width);
          root.current?.measureInWindow((x, y) => {
            origin.current = { x, y };
          });
        }}
      >
        <View
          style={s.root}
          pointerEvents={selected ? 'none' : 'auto'}
          accessibilityElementsHidden={!!selected}
          importantForAccessibility={selected ? 'no-hide-descendants' : 'auto'}
        >
          <Text style={s.toolbar}>Trail catalogue</Text>
          <View style={s.search}>
            <TextInput
              accessibilityLabel="Search products"
              testID="search-products"
              placeholder="Search products"
              autoCorrect={false}
              autoCapitalize="none"
              value={draft}
              onChangeText={setDraft}
              style={s.input}
            />
            <Pressable
              accessibilityRole="button"
              onPress={() => {
                setQuery(draft);
                Keyboard.dismiss();
              }}
              style={s.action}
            >
              <Text style={s.button}>Search</Text>
            </Pressable>
          </View>
          <View style={s.filter}>
            <Pressable
              accessibilityRole="checkbox"
              accessibilityState={{ checked: only }}
              onPress={() => setOnly(!only)}
            >
              <Text>{only ? '☑' : '☐'} Favorites only</Text>
            </Pressable>
            <Pressable
              accessibilityRole="button"
              onPress={() => {
                setDraft('');
                setQuery('');
                setOnly(false);
              }}
            >
              <Text style={s.button}>Clear filters</Text>
            </Pressable>
          </View>
          {!!error && <Text accessibilityRole="alert">{error}</Text>}
          <FlatList
            data={data}
            keyExtractor={p => p.id}
            removeClippedSubviews={false}
            initialNumToRender={4}
            ListEmptyComponent={<Text style={s.empty}>No products found</Text>}
            renderItem={({ item: p }) => (
              <View style={s.card}>
                <Pressable
                  accessibilityLabel={`Open ${p.id}`}
                  accessibilityRole="button"
                  onPress={() => open(p)}
                >
                  <View
                    ref={v => {
                      imageRefs.current[p.id] = v;
                    }}
                    collapsable={false}
                  >
                    <Image
                      source={images[p.imageKey]}
                      resizeMode="cover"
                      style={[
                        s.image,
                        { opacity: selected?.id === p.id ? 0 : 1 },
                      ]}
                    />
                  </View>
                </Pressable>
                <Pressable accessible={false} onPress={() => open(p)}>
                  <View style={s.cardText}>
                    <Text style={s.title}>{p.name}</Text>
                    <Text style={s.caption}>
                      {p.category} · {price(p.priceCents)}
                    </Text>
                  </View>
                </Pressable>
                {star(p)}
              </View>
            )}
          />
        </View>
        {selected && (
          <View style={StyleSheet.absoluteFill} accessibilityViewIsModal>
            <View
              style={[
                StyleSheet.absoluteFill,
                { backgroundColor: 'white', opacity: progress },
              ]}
            />
            <Image
              source={images[selected.imageKey]}
              resizeMode="cover"
              style={{
                position: 'absolute',
                left: sourceExists ? mix(source.x, 0) : 0,
                top: sourceExists ? mix(source.y, 52) : 52,
                width: sourceExists ? mix(source.width, width) : width,
                height: sourceExists ? mix(source.height, 280) : 280,
                borderRadius: sourceExists ? 16 * (1 - progress) : 0,
                opacity: sourceExists ? 1 : progress,
              }}
            />
            <View style={{ opacity: Math.max(0, (time - 0.35) / 0.65) }}>
              <View style={s.detailBar}>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Back"
                  onPress={close}
                >
                  <Text style={s.button}>‹ Back</Text>
                </Pressable>
              </View>
              <View style={s.detailText}>
                <Text style={s.detailTitle}>{selected.name}</Text>
                <Text style={s.caption}>
                  {selected.category} · {price(selected.priceCents)}
                </Text>
                <Text style={s.description}>{selected.description}</Text>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`Favorite ${selected.id}`}
                  onPress={() => toggle(selected.id)}
                >
                  <Text style={s.button}>
                    {favorites.includes(selected.id)
                      ? 'Remove favorite'
                      : 'Add favorite'}
                  </Text>
                </Pressable>
              </View>
            </View>
          </View>
        )}
        {/* CAPTURE_BEGIN */}
        <Text
          style={{ position: 'absolute', bottom: 44, left: 16 }}
        >{`Motion: ${reduced ? 'reduced' : 'animated'}`}</Text>
        <View
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 40,
            backgroundColor: 'white',
            flexDirection: 'row',
            justifyContent: 'space-around',
          }}
        >
          {[0, 0.25, 0.5, 0.75, 1].map(t => (
            <Pressable
              key={t}
              accessibilityLabel={`Capture ${t * 100}`}
              onPress={() => setCaptureTime(t)}
            >
              <Text>{t * 100}%</Text>
            </Pressable>
          ))}
        </View>
        {/* CAPTURE_END */}
      </View>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: 'white' },
  root: { flex: 1 },
  toolbar: {
    height: 52,
    paddingHorizontal: 16,
    paddingTop: 14,
    fontSize: 20,
    fontWeight: '600',
  },
  search: { height: 44, flexDirection: 'row', paddingHorizontal: 16, gap: 8 },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#888',
    borderRadius: 8,
    paddingHorizontal: 10,
    fontSize: 16,
    paddingVertical: 0,
  },
  action: { justifyContent: 'center', paddingHorizontal: 8 },
  button: { color: '#235a45', fontSize: 16 },
  filter: {
    height: 40,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  card: { marginHorizontal: 16, marginBottom: 16 },
  image: { height: 180, width: '100%', borderRadius: 16 },
  cardText: { height: 72, paddingTop: 12 },
  title: { fontSize: 18, color: '#17271f' },
  caption: { fontSize: 14, color: '#47564d', marginTop: 4 },
  favorite: { position: 'absolute', right: 0, bottom: 12, padding: 12 },
  empty: { padding: 32, textAlign: 'center' },
  detailBar: { height: 52, padding: 16 },
  detailText: { marginTop: 280, padding: 16 },
  detailTitle: { fontSize: 24, color: '#17271f' },
  description: { fontSize: 16, marginVertical: 16, color: '#17271f' },
});
export default function App() {
  return (
    <SafeAreaProvider>
      <Catalogue />
    </SafeAreaProvider>
  );
}

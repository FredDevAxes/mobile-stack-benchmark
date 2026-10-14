export type Product = {
  id: string;
  name: string;
  category: string;
  priceCents: number;
  description: string;
  imageKey: string;
};
export const products: Product[] = require('../assets/products.json');
export const filtered = (query: string, only: boolean, favorites: string[]) =>
  products.filter(
    p =>
      p.name.toLowerCase().includes(query.toLowerCase()) &&
      (!only || favorites.includes(p.id)),
  );
export const price = (cents: number) => `€${(cents / 100).toFixed(2)}`;
export const toggled = (ids: string[], id: string) =>
  ids.includes(id) ? ids.filter(x => x !== id) : [...ids, id];

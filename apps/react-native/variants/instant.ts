import { useEffect } from 'react';
export function useProgress(
  target: number,
  _reduced: boolean,
  done: (target: number) => void,
): [number, number] {
  useEffect(() => {
    done(target);
  }, [target, done]);
  return [target, target];
}

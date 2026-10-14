import { useEffect, useRef, useState } from 'react';
import { Animated, Easing } from 'react-native';
const curve = Easing.bezier(0.4, 0, 0.2, 1);
export function useProgress(
  target: number,
  reduced: boolean,
  done: (target: number) => void,
): [number, number] {
  const clock = useRef(new Animated.Value(0)).current;
  const [time, setTime] = useState(0);
  useEffect(() => {
    const listener = clock.addListener(({ value }) => setTime(value));
    Animated.timing(clock, {
      toValue: target,
      duration: reduced ? 0 : 400,
      easing: Easing.linear,
      useNativeDriver: false,
    }).start(({ finished }) => {
      if (finished) {
        done(target);
      }
    });
    return () => {
      clock.removeListener(listener);
      clock.stopAnimation();
    };
  }, [clock, target, reduced, done]);
  return [curve(time), time];
}

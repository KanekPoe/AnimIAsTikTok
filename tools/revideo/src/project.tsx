/** Escena de prueba: un círculo que crece y un texto. Sirve para comprobar el render. */
import {makeProject, createRef, waitFor, all} from '@revideo/core';
import {makeScene2D, Circle, Txt} from '@revideo/2d';

const scene = makeScene2D('prueba', function* (view) {
  view.fill('#0E1018');
  const c = createRef<Circle>();
  const t = createRef<Txt>();
  view.add(<Circle ref={c} size={160} fill={'#FFC21A'} />);
  view.add(<Txt ref={t} y={500} fill={'white'} fontSize={90} fontWeight={900} text={'Newton Bien Loco'} opacity={0} />);
  yield* all(c().size(520, 1), t().opacity(1, 1));
  yield* waitFor(0.5);
});

export default makeProject({
  scenes: [scene],
  settings: {shared: {size: {x: 1080, y: 1920}}},
});

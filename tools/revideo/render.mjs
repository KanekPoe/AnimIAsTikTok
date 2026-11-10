// Render sin pantalla. Uso: node render.mjs [src/project.tsx] [salida.mp4]
import {renderVideo} from '@revideo/renderer';

const [projectFile = './src/project.tsx', outFile = 'prueba.mp4'] = process.argv.slice(2);
const chrome = process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome';

await renderVideo({
  projectFile,
  settings: {
    outFile,
    outDir: './output',
    logProgress: true,
    puppeteer: {executablePath: chrome, args: ['--no-sandbox', '--disable-gpu']},
  },
});
console.log('Render listo:', outFile);
process.exit(0); // el renderizador deja procesos abiertos

// Optional artwork export. Requires sharp; the skill itself remains dependency-free.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const require = createRequire(import.meta.url);
const sharp = require(process.env.SHARP_MODULE_PATH || 'sharp');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const jobs = [
  ['docs/preview-desktop.svg','docs/preview-desktop.png',2880,192],
  ['docs/logo-preview.svg','docs/logo-preview.png',2560,192],
  ['skills/claim-atlas/assets/logo-mark.svg','skills/claim-atlas/assets/logo-mark.png',1024,1536],
  ['skills/claim-atlas/assets/logo-lockup.svg','skills/claim-atlas/assets/logo-lockup.png',2040,432],
  ['skills/claim-atlas/assets/logo-lockup-dark.svg','skills/claim-atlas/assets/logo-lockup-dark.png',2040,432],
];
for (const [source,target,width,density] of jobs) {
  await sharp(path.join(root,source),{density}).resize({width}).png({compressionLevel:9}).toFile(path.join(root,target));
  const info = await sharp(path.join(root,target)).metadata();
  console.log(`${target}: ${info.width} x ${info.height}, ${info.format}`);
}
// Keep the actual phone capture at its native size; this does not restore lost detail.
await sharp(path.join(root,'docs/screenshots/preview-mobile.jpg')).png().toFile(path.join(root,'docs/preview-mobile.png'));

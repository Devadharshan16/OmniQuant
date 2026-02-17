const fs = require('fs');
const path = require('path');

// Copy service worker, manifest, and icons to build folder
const files = [
  { src: 'public/service-worker.js', dest: 'build/service-worker.js' },
  { src: 'public/manifest.json', dest: 'build/manifest.json' },
  { src: 'public/icon-192.png', dest: 'build/icon-192.png' },
  { src: 'public/icon-512.png', dest: 'build/icon-512.png' },
  { src: 'public/icon.svg', dest: 'build/icon.svg' }
];

files.forEach(({ src, dest }) => {
  const srcPath = path.join(__dirname, src);
  const destPath = path.join(__dirname, dest);
  
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    console.log(`✓ Copied ${src} to ${dest}`);
  } else {
    console.warn(`⚠ Warning: ${src} not found`);
  }
});

console.log('✓ All PWA files copied to build folder');

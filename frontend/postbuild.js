const fs = require('fs');
const path = require('path');

// Copy service worker and manifest to build folder
const files = [
  { src: 'public/service-worker.js', dest: 'build/service-worker.js' },
  { src: 'public/manifest.json', dest: 'build/manifest.json' }
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

console.log('✓ PWA files copied to build folder');

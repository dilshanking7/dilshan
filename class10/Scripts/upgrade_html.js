// One-time migration: replaces the static <header class="navbar">...</header>
// block with the central placeholder and injects js/lang.js on every page.
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, '..', 'website');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));

for (const f of files) {
  const fp = path.join(dir, f);
  let html = fs.readFileSync(fp, 'utf8');

  const headerRep = /<header class="navbar">[\s\S]*?<\/header>/;
  if (headerRep.test(html)) {
    html = html.replace(headerRep, '<header class="navbar" id="siteHeader"></header>');
  }

  if (!html.includes('js/lang.js')) {
    html = html.replace('</body>', '<script src="js/lang.js"></script>\n</body>');
  }

  fs.writeFileSync(fp, html, 'utf8');
  console.log('OK', f);
}
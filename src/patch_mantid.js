const { applyPatch, parsePatch } = require('diff');
const fs = require('fs');
const path = require('node:path');

const diffdir = 'diffs';
const srcdir = 'mantid';
const destdir = 'py_src';

// Reads in the patches
const patches = fs.readdirSync(diffdir).map(
  file => {
    const diffile = fs.readFileSync(diffdir + '/' + file).toString();
    return parsePatch(diffile);
  }
).reduce((l0, l1) => l0.concat(l1));

// Copies original files over and patch them if needed
fs.readdirSync(srcdir, { recursive: true }).map(
  file => {
    const destfile = destdir + '/' + file.replaceAll('\\', '/');
    const subdir = path.dirname(destfile);
    if (!fs.existsSync(subdir)) {
      try {
        fs.mkdirSync(subdir, { recursive: true });
      } catch {
        fs.mkdirSync(subdir);
      }
    }
    const patch = patches.map(
      patch => (destfile == patch.newFileName) ? patch : {}
    ).reduce((l0, l1) => { return {...l0, ...l1} });
    if (Object.hasOwn(patch, 'hunks')) {
      const origFile = fs.readFileSync(srcdir + '/' + file).toString();
      const patchedFile = applyPatch(origFile, patch);
      fs.writeFileSync(destfile, patchedFile);
    } else {
      fs.copyFile(srcdir + '/' + file, destfile, (err) => {});
    }
  }
);

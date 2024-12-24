// Basic MIME types
const mimedict = {
  css: "text/css",
  gif: "image/gif",
  htm: "text/html", html: "text/html",
  ico: "image/x-icon",
  jpg: "image/jpg", jpeg: "image/jpg",
  js: "application/javascript",
  json: "application/json",
  png: "image/png",
  svg: "image/svg+xml",
  txt: "text/plain",
  xml: "application/xml",
  mp3: "audio/mpeg",
  py: "text/x-python"
}

const stripPrefix = path => path.split(":").splice(1).join("");
function stp(path) {
  if (typeof path === 'string' || path instanceof String) {
    return stripPrefix(path);
  } else {
    return stripPrefix(path.path);
  }
}

function get_mime(path) {
  const ext = stp(path).split('.').reverse().at(0);
  return ext in mimedict ? mimedict[ext] : "application/octet-stream";
}

function get_stat(path, fs) {
  const em_stat = fs.stat(stp(path));
  return {
    isDirectory: fs.isDir(em_stat.mode),
    isFile: fs.isFile(em_stat.mode),
    mime: get_mime(path),
    size: em_stat.size,
    path: path,
    filename: path.split('/').reverse().at(0),
    id: em_stat.ino,
    parent_id: em_stat.dev,
    stat: em_stat
  }
};

async function readFile(path, type, options) {
  const fs = window.pyodide.FS;
  if (type == "string") {
    return {body: fs.readFile(stp(path), {encoding: 'utf8'}), mime: 'text/plain'};
  } else {
    return {body: fs.readFile(stp(path), {encoding: 'binary'}), mime: get_mime(path)};
  }
};

export default function EmscriptenFSAdapter(core) {
  const fs = window.pyodide.FS;
  return {
    readdir: async function(path, options) {
      return Array.from(fs.readdir(stp(path)).filter((x) => x != "." && x != ".."), (x) => get_stat(path.path+"/"+x, fs));
    },
    readfile: readFile,
    writefile: async function(path, data, options) {
      if (typeof data === 'string' || data instanceof String) {
        return fs.writeFile(stp(path), data);
      } else {
        const arrayBuf = await data.arrayBuffer();
        return fs.writeFile(stp(path), new Uint8Array(arrayBuf));
      }
    },
    copy: (from, to, options) => Promise.resolve(fs.writeFile(stp(to), fs.readFile(stp(from)))),
    rename: (from, to, options) => Promise.resolve(fs.rename(stp(from), stp(to))),
    mkdir: (path, options) => Promise.resolve(fs.mkdir(stp(path))),
    unlink: (path, options) => Promise.resolve(fs.unlink(stp(path))),
    exists: (path, options) => Promise.resolve(fs.analyzePath(stp(path)).exists),
    mount: options => Promise.resolve(true),
    unmount: options => Promise.resolve(true),
    stat: (path, options) => Promise.resolve(get_stat(path, fs)),
    url: async function(path, options) {
      const data = await readFile(path, 'blob');
      return window.URL.createObjectURL(new Blob(data.body, {type: data.mime}));
    },
    search: (root, pattern, options) => Promise.resolve([]),
    touch: (path, options) => Promise.resolve(fs.close(fs.open(stp(path), 'a')))
  };
};

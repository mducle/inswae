const admzip = require("adm-zip");

const zip = new admzip();
zip.addLocalFolder(process.argv.slice(-2,-1)[0], ".");
zip.writeZip(process.argv.slice(-1)[0]);

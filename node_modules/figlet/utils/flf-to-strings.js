var path = require('path');
var fontDir = path.join(__dirname, '/../fonts/');
var exportDir = path.join(__dirname, '../importable-fonts/');
var fs = require('fs')

fs.readdir(fontDir, function (err, files) {
    if (err) {
        console.error(err);
        return;
    }

    files.forEach( function (name) {
        if ( /\.flf$/.test(name) ) {
            console.log(name);
            var fontData = fs.readFileSync( path.join(fontDir, name),  {encoding: 'utf-8'});
            fontData = 'export default `' + fontData.replace(/\\/g, '\\\\').replace(/`/g, '\\`') + '`';
            fs.writeFileSync( path.join(exportDir, name.replace(/flf$/, 'js') ), fontData, {encoding: 'utf-8'});

        }
    });

});
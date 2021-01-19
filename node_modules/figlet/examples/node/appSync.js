/*
 Example
 */

var figlet = require('../../lib/node-figlet.js');

/*
 Once this has been run:

 npm install figlet

 Use the below line instead of the above line
 */
// var figlet = require('figlet');

console.log(figlet.textSync('Hello World!', 'Standard'));
console.log(figlet.textSync('Again, Hello World!', 'Graffiti'));
console.log(figlet.textSync('Last time...', {
    font: 'Standard',
    horizontalLayout: 'full',
    verticalLayout: 'full'
}));
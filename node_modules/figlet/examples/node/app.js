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

figlet('Hello World!', 'Standard', function(err, data) {
    if (err) {
        console.log('Something went wrong...');
        console.dir(err);
        return;
    }

    console.log(data);

    figlet.text('Again, Hello World!', 'Graffiti', function(err, data) {
        if (err) {
            console.log('Something went wrong...');
            console.dir(err);
            return;
        }

        console.log(data);

        figlet.text('Last time...', {
            font: 'Standard',
            horizontalLayout: 'full',
            verticalLayout: 'full'
        }, function(err, data) {
            if (err) {
                console.log('Something went wrong...');
                console.dir(err);
                return;
            }
            console.log(data);
        });

    });

});



'use strict';

var figlet = require('../lib/node-figlet'),
    grunt = require('grunt'),
    fs = require('fs'),
    path = require('path'),
    async = require('async');

/*
  ======== A Handy Little Nodeunit Reference ========
  https://github.com/caolan/nodeunit

  Test methods:
    test.expect(numAssertions)
    test.done()
  Test assertions:
    test.ok(value, [message])
    test.equal(actual, expected, [message])
    test.notEqual(actual, expected, [message])
    test.deepEqual(actual, expected, [message])
    test.notDeepEqual(actual, expected, [message])
    test.strictEqual(actual, expected, [message])
    test.notStrictEqual(actual, expected, [message])
    test.throws(block, [error], [message])
    test.doesNotThrow(block, [error], [message])
    test.ifError(value)
*/

exports.figlet = {
    setUp: function(done) {
        // setup here if necessary
        done();
    },
    standard: function(test) {
        test.expect(1);

        figlet('FIGlet\nFONTS', {
            font: 'Standard',
            verticalLayout: 'fitted'
        }, function(err, actual) {
            var expected = grunt.file.read('test/expected/standard');
            test.equal(actual, expected, 'Standard font with a vertical layout of "fitted".');

            test.done();
        });
    },
    standardSync: function(test) {
        test.expect(1);

        var expected = grunt.file.read('test/expected/standard');
        var actual = figlet.textSync('FIGlet\nFONTS', {font: 'Standard', verticalLayout: 'fitted'});

        test.equal(actual, expected, 'Standard font with a vertical layout of "fitted".');

        test.done();
    },
    standardParse: function(test) {
        test.expect(1);

        var expected = grunt.file.read('test/expected/standard');
        var data = fs.readFileSync(path.join(__dirname, '../fonts/Standard.flf'), 'utf8');
        var font = figlet.parseFont('StandardParseFontName', data);
        var actual = figlet.textSync('FIGlet\nFONTS', {font: 'StandardParseFontName', verticalLayout: 'fitted'});

        test.equal(actual, expected, 'Standard font with a vertical layout of "fitted" loaded using parseFont().');

        test.done();
    },
    graffiti: function(test) {
        test.expect(1);

        figlet.text('ABC.123', {
            font: 'Graffiti',
            horizontalLayout: 'fitted'
        }, function(err, actual) {
            var expected = grunt.file.read('test/expected/graffiti');
            test.equal(actual, expected, 'Graffiti font with a horizontal layout of "fitted".');

            test.done();
        });
    },
    graffitiSync: function(test) {
        test.expect(1);

        var expected = grunt.file.read('test/expected/graffiti');
        var actual = figlet.textSync('ABC.123', {font: 'Graffiti', horizontalLayout: 'fitted'});
        test.equal(actual, expected, 'Graffiti font with a horizontal layout of "fitted".');

        test.done();
    },
    wrap: function(test) {
        test.expect(4);
        var specs = [
            {
                input: 'Hello From The Figlet Library',
                expected: grunt.file.read('test/expected/wrapSimple')
            },
            {
                input: 'Hello From The Figlet Library That Wrap Text',
                expected: grunt.file.read('test/expected/wrapSimpleThreeLines')
            }
        ];
        (function recur() {
            var spec = specs.pop();
            if (!spec) {
                test.done();
            } else {
                figlet(spec.input, {
                    font: 'Standard',
                    width: 80
                }, function(err, actual) {
                    var maxWidth = actual.split('\n').reduce(function(acc, line) {
                        if (acc < line.length) {
                            return line.length;
                        }
                        return acc;
                    }, 0);
                    test.equal(maxWidth <= 80, true);
                    test.equal(actual, spec.expected, 'Standard font with wrap.');
                    recur();
                });
            }
        })();
    },
    wrapBreakWord: function(test) {
        test.expect(10);
        var specs = [
            {
                input: 'Hello From The Figlet Library',
                expected: grunt.file.read('test/expected/wrapWord'),
                width: 80
            },
            {
                input: 'Hello From The Figlet Library That Wrap Text',
                expected: grunt.file.read('test/expected/wrapWordThreeLines'),
                width: 80
            },
            {
                input: 'Hello From The Figlet Library That Wrap Text',
                expected: grunt.file.read('test/expected/wrapWordThreeLines'),
                width: 80
            },
            {
                input: 'Hello LongLongLong Word Longerhello',
                expected: grunt.file.read('test/expected/wrapWhitespaceBreakWord'),
                width: 30
            },
            {
                input: 'xxxxxxxxxxxxxxxxxxxxxxxx',
                expected: grunt.file.read('test/expected/wrapWhitespaceLogString'),
                width: 30
            }
        ];
        (function recur() {
            var spec = specs.pop();
            if (!spec) {
                test.done();
            } else {
                var width = spec.width;
                figlet(spec.input, {
                    font: 'Standard',
                    width: width,
                    whitespaceBreak: true
                }, function(err, actual) {
                    var maxWidth = actual.split('\n').reduce(function(acc, line) {
                        if (acc < line.length) {
                            return line.length;
                        }
                        return acc;
                    }, 0);
                    test.equal(maxWidth <= width, true);
                    test.equal(actual, spec.expected, 'Standard font with word break.');
                    recur();
                });
            }
        })();
    },
    dancingFont: function(test) {
        test.expect(1);

        figlet.text('pizzapie', {
            font: 'Dancing Font',
            horizontalLayout: 'full'
        }, function(err, actual) {

            var expected = grunt.file.read('test/expected/dancingFont');
            test.equal(actual, expected, 'Dancing Font with a horizontal layout of "full".');

            test.done();
        });
    },
    dancingFontSync: function(test) {
        test.expect(1);

        var expected = grunt.file.read('test/expected/dancingFont');
        var actual = figlet.textSync('pizzapie', {font: 'Dancing Font', horizontalLayout: 'full'});
        test.equal(actual, expected, 'Dancing Font with a horizontal layout of "full".');

        test.done();
    },
    printDirection: function(test) {
        test.expect(1);

        figlet.text('pizzapie', {
            font: 'Dancing Font',
            horizontalLayout: 'full',
            printDirection: 1
        }, function(err, actual) {

            var expected = grunt.file.read('test/expected/dancingFontReverse');
            test.equal(actual, expected, 'Dancing Font with a reversed print direction.');

            test.done();
        });
    },
    /*
        This test ensures that all fonts will load without error
    */
    loadAll: function(test) {
        var errCount = 0;
        test.expect(1);

        figlet.fonts(function(err, fonts) {
            if (err) {
                errCount++;
                return;
            }

            async.eachSeries(fonts, function(font, next) {
                figlet.text('abc ABC ...', {
                    font: font
                }, function(err, data) {
                    if (err) {
                        errCount++;
                    }
                    next();
                });
            }, function(err) {
                test.equal(errCount, 0, 'A problem occurred while testing one of the fonts.');
                test.done();
            });
        });
    }
};

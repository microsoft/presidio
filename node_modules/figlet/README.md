```
___________.___  ________.__          __          __        
\_   _____/|   |/  _____/|  |   _____/  |_       |__| ______
 |    __)  |   /   \  ___|  | _/ __ \   __\      |  |/  ___/
 |     \   |   \    \_\  \  |_\  ___/|  |        |  |\___ \
 \___  /   |___|\______  /____/\___  >__| /\ /\__|  /____  >
     \/                \/          \/     \/ \______|    \/

```
[![Build Status](https://travis-ci.org/patorjk/figlet.js.svg)](https://travis-ci.org/patorjk/figlet.js)

This project aims to fully implement the FIGfont spec in JavaScript. It works in the browser and with Node.js. You can see it in action here: http://patorjk.com/software/taag/ (the figlet.js file was written to power that application)

Quick Start - Node.js
-------------------------

Install:

```sh
npm install figlet
```

Simple usage:

```js
var figlet = require('figlet');

figlet('Hello World!!', function(err, data) {
    if (err) {
        console.log('Something went wrong...');
        console.dir(err);
        return;
    }
    console.log(data)
});
```

That should print out:

```
  _   _      _ _        __        __         _     _ _ _
 | | | | ___| | | ___   \ \      / /__  _ __| | __| | | |
 | |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` | | |
 |  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |_|_|
 |_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_(_|_)
```

Basic Usage - Node.js
-------------------------

### text

Calling the figlet object as a function is shorthand for calling the text function. This method allows you to create ASCII Art from text. It takes in 3 parameters:

* Input Text - A string of text to turn into ASCII Art.
* Options - Either a string indicating the font name or an options object (description below).
* Callback - A function to execute with the generated ASCII Art.

Example:

```js
figlet.text('Boo!', {
    font: 'Ghost',
    horizontalLayout: 'default',
    verticalLayout: 'default',
    width: 80,
    whitespaceBreak: true
}, function(err, data) {
    if (err) {
        console.log('Something went wrong...');
        console.dir(err);
        return;
    }
    console.log(data);
});
```

That will print out:

```
.-. .-')                            ,---.
\  ( OO )                           |   |
 ;-----.\  .-'),-----.  .-'),-----. |   |
 | .-.  | ( OO'  .-.  '( OO'  .-.  '|   |
 | '-' /_)/   |  | |  |/   |  | |  ||   |
 | .-. `. \_) |  |\|  |\_) |  |\|  ||  .'
 | |  \  |  \ |  | |  |  \ |  | |  |`--'  
 | '--'  /   `'  '-'  '   `'  '-'  '.--.  
 `------'      `-----'      `-----' '--'
```

### textSync

This method is the synchronous version of the method above.

* Input Text - A string of text to turn into ASCII Art.
* Font Options - Either a string indicating the font name or an options object (description below).

Example:

```js
console.log(figlet.textSync('Boo!', {
    font: 'Ghost',
    horizontalLayout: 'default',
    verticalLayout: 'default',
    width: 80,
    whitespaceBreak: true
}));
```

That will print out:

```
.-. .-')                            ,---.
\  ( OO )                           |   |
 ;-----.\  .-'),-----.  .-'),-----. |   |
 | .-.  | ( OO'  .-.  '( OO'  .-.  '|   |
 | '-' /_)/   |  | |  |/   |  | |  ||   |
 | .-. `. \_) |  |\|  |\_) |  |\|  ||  .'
 | |  \  |  \ |  | |  |  \ |  | |  |`--'
 | '--'  /   `'  '-'  '   `'  '-'  '.--.
 `------'      `-----'      `-----' '--'
```

### Options

The options object has several parameters which you can set:

#### font
Type: `String`
Default value: `'Standard'`

A string value that indicates the FIGlet font to use.

#### horizontalLayout
Type: `String`
Default value: `'default'`

A string value that indicates the horizontal layout to use. FIGlet fonts have 5 possible values for this: "default", "full", "fitted", "controlled smushing", and "universal smushing". "default" does the kerning the way the font designer intended, "full" uses full letter spacing, "fitted" moves the letters together until they almost touch, and "controlled smushing" and "universal smushing" are common FIGlet kerning setups.

#### verticalLayout
Type: `String`
Default value: `'default'`

A string value that indicates the vertical layout to use. FIGlet fonts have 5 possible values for this: "default", "full", "fitted", "controlled smushing", and "universal smushing". "default" does the kerning the way the font designer intended, "full" uses full letter spacing, "fitted" moves the letters together until they almost touch, and "controlled smushing" and "universal smushing" are common FIGlet kerning setups.

#### width
Type: `Number`
Default value: `undefined`

This option allows you to limit the width of the output. For example, if you want your output to be a max of 80 characters wide, you would set this option to 80. [Example](https://github.com/patorjk/figlet.js/blob/master/examples/front-end/index.htm)

#### whitespaceBreak
Type: `Boolean`
Default value: `false`

This option works in conjunction with "width". If this option is set to true, then the library will attempt to break text up on whitespace when limiting the width. [Example](https://github.com/patorjk/figlet.js/blob/master/examples/front-end/index.htm)

### Understanding Kerning

The 2 layout options allow you to override a font's default "kerning". Below you can see how this effects the text. The string "Kerning" was printed using the "Standard" font with horiontal layouts of "default", "fitted" and then "full". 

```
  _  __               _             
 | |/ /___ _ __ _ __ (_)_ __   __ _
 | ' // _ \ '__| '_ \| | '_ \ / _` |
 | . \  __/ |  | | | | | | | | (_| |
 |_|\_\___|_|  |_| |_|_|_| |_|\__, |
                              |___/
  _  __                   _               
 | |/ / ___  _ __  _ __  (_) _ __    __ _
 | ' / / _ \| '__|| '_ \ | || '_ \  / _` |
 | . \|  __/| |   | | | || || | | || (_| |
 |_|\_\\___||_|   |_| |_||_||_| |_| \__, |
                                    |___/
  _  __                        _                 
 | |/ /   ___   _ __   _ __   (_)  _ __     __ _
 | ' /   / _ \ | '__| | '_ \  | | | '_ \   / _` |
 | . \  |  __/ | |    | | | | | | | | | | | (_| |
 |_|\_\  \___| |_|    |_| |_| |_| |_| |_|  \__, |
                                           |___/
```

In most cases you'll either use the default setting or the "fitted" setting. Most fonts don't support vertical kerning, but a hand full fo them do (like the "Standard" font).

### metadata

The metadata function allows you to retrieve a font's default options and header comment. Example usage:

```js
figlet.metadata('Standard', function(err, options, headerComment) {
    if (err) {
        console.log('something went wrong...');
        console.dir(err);
        return;
    }
    console.dir(options);
    console.log(headerComment);
});
```

### fonts

The fonts function allows you to get a list of all of the available fonts. Example usage:

```js
figlet.fonts(function(err, fonts) {
    if (err) {
        console.log('something went wrong...');
        console.dir(err);
        return;
    }
    console.dir(fonts);
});
```

### fontsSync

The synchronous version of the fonts method

```js
console.log(figlet.fontsSync());
```

### parseFont

Allows you to use a font from another source.

```js
const fs = require('fs');
const path = require('path');

let data = fs.readFileSync(path.join(__dirname, 'myfont.flf'), 'utf8');
figlet.parseFont('myfont', data);
console.log(figlet.textSync('myfont!', 'myfont'));
```

Getting Started - Webpack / React
-------------------------

Webpack/React usage will be very similar to what's talked about in the "Getting Started - The Browser" section. The main difference is that you import fonts via the importable-fonts folder. Example:

```js
import figlet from 'figlet';
import standard from 'figlet/importable-fonts/Standard.js'

figlet.parseFont('Standard', standard);

figlet.text('test', {
    font: 'Standard',
}, function(err, data) {
    console.log(data);
});
```

Getting Started - The Browser
-------------------------

The browser API is the same as the Node API with the exception of the "fonts" method not being available. The browser version also requires [fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) (or a [shim](https://github.com/github/fetch)) for its loadFont function.

Example usage:

```html
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/fetch/1.0.0/fetch.min.js"></script>
<script type="text/javascript" src="figlet.js"></script>

<script>

    figlet(inputText, 'Standard', function(err, text) {
        if (err) {
            console.log('something went wrong...');
            console.dir(err);
            return;
        }
        console.log(text);
    });

</script>
```

### textSync

The browser API supports a synchronous mode so long as fonts used are preloaded.

Example:

```js
figlet.defaults({fontPath: "assets/fonts"});

figlet.preloadFonts(["Standard", "Ghost"], ready);

function ready(){
  console.log(figlet.textSync("ASCII"));
  console.log(figlet.textSync("Art", "Ghost"));
}

```

That will print out:

```
     _     ____    ____  ___  ___
    / \   / ___|  / ___||_ _||_ _|
   / _ \  \___ \ | |     | |  | |
  / ___ \  ___) || |___  | |  | |
 /_/   \_\|____/  \____||___||___|

   ('-.     _  .-')   .-') _    
  ( OO ).-.( \( -O ) (  OO) )   
  / . --. / ,------. /     '._  
  | \-.  \  |   /`. '|'--...__)
.-'-'  |  | |  /  | |'--.  .--'
 \| |_.'  | |  |_.' |   |  |    
  |  .-.  | |  .  '.'   |  |    
  |  | |  | |  |\  \    |  |    
  `--' `--' `--' '--'   `--'    

```

See the examples folder for a more robust front-end example.

Getting Started - Command Line
-------------------------

To use figlet.js on the command line, install figlet-cli:

```sh
npm install -g figlet-cli
```

And then you should be able run from the command line. Example:

```sh
figlet -f "Dancing Font" "Hi"
```

For more info see the [figlet-cli](https://github.com/patorjk/figlet-cli).

## Release History
* 2020.07.12 v1.5.0 Added width and whitespaceBreak options.
* 2020.04.26 v1.4.0 Removed jQuery from preloader and examples.
* 2020.02.23 v1.3.0 Added the "ANSI Regular" font and updated the README with info on how to use with Webpack.
* 2018.03.26 v1.2.1 parseFont works in node for adding fonts manually
* 2016.09.27 v1.2.0 jQuery replaced with fetch API / polyfill.
* 2016.04.28 v1.1.2 textSync now works in the browser with font pre-loading.
* 2013.01.02 v1.0.8 Added tests and command line info.
* 2013.12.28 v1.0.7 README update and minor tweaks.
* 2014.07.31 v1.0.1 Bug fixes.
* 2014.08.15 v1.1.0 Sync functions added.

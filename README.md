# warhol

A small server and browser extension pairing that allows for adding styles
and scripts to a page on the fly. Supports JavaScript, CSS. Allows for direct
conversion from an 'extension' language such as Sass, LESS, or Coffeescript.

This extension draws on work and concepts from several previous extensions,
namely:
* [dotjs][dotjs]
* [dotcss][dotcss]
* [Greasemonkey][greasemonkey]
* [Stylish][stylish]

[dotjs]: https://github.com/defunkt/dotjs
[dotcss]: https://github.com/stewart/dotcss/
[greasemonkey]: https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/
[stylish]: https://chrome.google.com/webstore/detail/stylish/fjnbnpbmkenffdnngjfgmeleoegfcffe?hl=en

## Installation

Open a terminal and check out the warhol repoitory:

    $ git clone https://github.com/dhaffner/warhol
    $ cd warhol

#### Server

Install the server portion of warhol via `make`.

    $ make server


#### Extension

The Google Chrome extension can be installed manually:
1. Navigate to [chrome://extesion/](chrome://extesion/)
2. Check the box labeled 'Developer Mode'
3. Click 'Load unpacked extension' and select the `chrome` folder
under your warhol directory.

An alternative method for installing the extension is available via `make`:

    $ make extension

This will:
* Pack the `chrome` directory into a .crx
* Install it as an [external extension](http://developer.chrome.com/extensions/external_extensions.html)
* Remove any previous installs of the same .crx file
* Relaunch Chrome

The `make-extension` script is provided as a convenience but can be
easily edited to use alternative paths.


## Usage


Ensure that warhol.py is executable:

    chmod +x warhol.py


To run the server using the default configuration file. (~/.warhol/config)

    ./warhol.py


To run the server using a specified configuration file.

    ./warhol.py <config>


To run a check on a specified configuration, and run the server using that
configuration:

    ./warhol.py --check <config>


To only run a check on the specified configuration.

    ./warhol check <config>

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

## INSTALLATION

    $ git clone https://github.com/dhaffner/warhol
    $ cd warhol
    $ python setup.py install

Load the Chrome extension in Developer mode, click 'Load unpacked
extension...' and select the the 'chrome' directory under the
warhol folder.


## USAGE


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

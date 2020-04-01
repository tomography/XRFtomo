#!/bin/bash
mkdir -p "$PREFIX/Menu"
if [ $OSX_ARCH ]
then
    cp "$RECIPE_DIR/menu-osx.json" "$PREFIX/Menu"
    cp "$RECIPE_DIR/app.icns" "$PREFIX/Menu"
else
    cp "$RECIPE_DIR/menu-linux.json" "$PREFIX/Menu"
    cp "$RECIPE_DIR/app.svg" "$PREFIX/Menu"
fi

$PYTHON setup.py install || exit 1

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.

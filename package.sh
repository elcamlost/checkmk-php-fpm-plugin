#!/bin/bash

PKG_NAME="php_fpm"
TITLE="PHP-FPM monitoring"
AUTHOR="Ilya Rassadin elcamlost at gmail dot com"
DESCRIPTION="This check monitors performance indicators of php-fpm pools. See changes here https://raw.githubusercontent.com/elcamlost/checkmk-php-fpm-plugin/master/php-fpm/Changes"
DOWNLOAD_URL="https://github.com/elcamlost/checkmk-php-fpm-plugin"
PLUGIN_VERSION="2.1.0"
CHECKMK_MIN_VERSION="2.4.0p1"
CHECKMK_PKG_VERSION=$CHECKMK_MIN_VERSION

SOURCE_PATH="$(cd "$(dirname "$0")" && pwd)/php-fpm"
OUTPUT_PATH="$(cd "$(dirname "$0")" && pwd)"

# suppress macOS extended attributes in tar archives
export COPYFILE_DISABLE=1

# remove any python compiled binaries
find "$SOURCE_PATH" -name "*.pyc" -delete

# Create staging directory mirroring the package layout:
#   agents/plugins/...
#   cmk_addons_plugins/php_fpm/{agent_based,graphing,rulesets,checkman}/...
STAGING=$(mktemp -d)
trap "rm -rf $STAGING" EXIT

mkdir -p "$STAGING/cmk_addons_plugins/$PKG_NAME"
cp -r "$SOURCE_PATH/agents" "$STAGING/"
for dir in agent_based graphing rulesets checkman; do
    cp -r "$SOURCE_PATH/$dir" "$STAGING/cmk_addons_plugins/$PKG_NAME/"
done

cd "$STAGING"

filedict=""
numfiles=0

while read dir; do
    cd "$dir"

    dir_files="$(find -L -type f)"
    pretty_key=$(echo "$dir" | sed -E 's/\.\///g')

    tar --dereference -cf "$OUTPUT_PATH/$dir.tar" *
    cd - &>/dev/null

    filedict="$filedict'$pretty_key': ["

    first=1
    for file in $dir_files; do
        pretty_file=$(echo "$file" | sed -E 's/^\.\///g')
        if [ $first -eq 1 ]; then
            filedict="$filedict'$pretty_file'"
            first=0
        else
            filedict="$filedict,'$pretty_file'"
        fi
        numfiles=$(( numfiles + 1 ))
    done

    filedict="$filedict],"
done < <(find . -maxdepth 1 -type d -name "[!.]*")

filedict="${filedict%,}"

info="{'author': '$AUTHOR',
 'description': '$DESCRIPTION',
 'download_url': '$DOWNLOAD_URL',
 'files': {$filedict},
 'name': '$PKG_NAME',
 'num_files': $numfiles,
 'title': '$TITLE',
 'version': '$PLUGIN_VERSION',
 'version.min_required': '$CHECKMK_MIN_VERSION',
 'version.packaged': '$CHECKMK_PKG_VERSION',
 'version.usable_until': None}"

cd "$OUTPUT_PATH"
echo $info > info
echo $info | sed -E "s/'/"'"'"/g" > info.json

tar -c *.tar info info.json | gzip --best - > "$OUTPUT_PATH/${PKG_NAME}.mkp"

rm -f *.tar info info.json

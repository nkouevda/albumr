#!/bin/bash

# Nikita Kouevda
# 2012/12/26

# Store script name and directory
script_name="${0##*/}"
script_dir="${0%/*}"

# Prints usage
function usage () {
    echo "usage: $script_name [-h] [-v] [--] album ..."
}

# Prints help message
function help_message () {
    usage
    cat <<EOF
options:
    -h      Show this help message.
    -v      Enable verbose output.
EOF
}

# Returns 0 iff verbose output is enabled
function verbose () {
    [[ -n "$verbose_option" ]]
    return $?
}

# Iterate over options
while getopts "hv" option "$@"; do
    case "$option" in
        # Parsing error; print usage to stderr and exit
        \?)
            usage >&2
            exit 1
            ;;
        # Print help message and exit
        h)
            help_message
            exit 0
            ;;
        # Verbose output
        v)
            verbose_option=0
            ;;
    esac
done

# Set shell positional arguments to the remaining arguments
set -- ${@:$OPTIND}

# Print usage to stderr and exit if no positional arguments given
if [[ -z "$*" ]]; then
    usage >&2
    exit 1
fi

# Iterate over the given albums concurrently
for album in "$@"; do
    (
    # Print the album being processed
    verbose && echo "starting album: $album"

    # Determine the album hash
    if [[ -n "$(curl -sI -- "http://imgur.com/a/$album" | head -n 1 | grep 200)" ]]; then
        album_hash=${album:0:5}
    elif [[ -n "$(curl -sI -- "$album" | head -n 1 | grep 200)" ]]; then
        album_hash=$(echo "$album" | perl -ne 'm/imgur.com\/a\/([A-Za-z0-9]{5})/; print $1')
    else
        echo "error: could not read album: $album" >&2
        exit 1
    fi

    # Determine the album URL based on the hash
    album_url="http://imgur.com/a/$album_hash"

    # Print the album hash and URL
    verbose && echo "album hash: $album_hash"
    verbose && echo "album URL: $album_url"

    # Use the album hash to make the directory if necessary
    if [[ ! -e "$album_hash" ]]; then
        verbose && echo "making directory: $album_hash"
        mkdir "$album_hash"
    elif [[ ! -d "$album_hash" ]]; then
        echo "error: not a directory: $album_hash" >&2
        exit 1
    fi

    # Extract the image hashes and extensions
    images=$(curl -s "$album_url" | tr '}' '\n' | perl -ne 'print "$1$2\n" if m/"hash":"([A-Za-z0-9]{5})".+?"ext":"(.+?)"/')

    # Download and store the images concurrently
    for image in $images; do
        (
        # Strip any trailing characters for the local filename
        filename=$(echo $image | perl -pe 's/([A-Za-z0-9]\.[A-Za-z]{3,4}).*/$1/g')

        # Skip existing files
        if [[ -e "$album_hash/$filename" ]]; then
            verbose && echo "skipping existing file: $album_hash/$filename"
            exit 0
        fi

        # Download the image and save it, storing the return code of curl
        verbose && echo "downloading image: http://i.imgur.com/$image"
        curl -so "$album_hash/$filename" "http://i.imgur.com/$image"
        return_code=$?

        # Print success only if verbose output enabled
        verbose && [[ $return_code -eq 0 ]] && echo "saved image: $album_hash/$filename"

        # Print error message and remove the file if failed
        if [[ $return_code -ne 0 ]]; then
            echo "error: download or save failed: $image" >&2
            rm "$album_hash/$filename"
        fi
        ) &
    done

    # Wait for all images to download
    wait

    # Indicate album completion
    verbose && echo "finished album: $album"
    ) &
done

# Wait for all albums to finish
wait

# Indicate completion
verbose && echo "done"

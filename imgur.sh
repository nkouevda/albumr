#!/bin/bash

# Nikita Kouevda
# 2012/12/24

# Store script name and directory
script_name="${0##*/}"
script_dir="${0%/*}"

# Prints usage
function usage () {
    echo "usage: $script_name [-h] [-v] [--] [album ...]"
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
        # Parsing error; print usage and exit
        \?)
            usage
            exit 1
            ;;
        # Print help message and exit
        h)
            help_message
            exit 0
            ;;
        # Enable verbose output
        v)
            verbose_option=0
            ;;
    esac
done

# Set arguments to remaining positional arguments
set -- ${@:$OPTIND}

# Print usage and exit if no positional arguments given
if [[ -z "$*" ]]; then
    usage
    exit 0
fi

# Iterate over the given albums
for album in "$@"; do
    # Print the album being processed
    verbose && echo "processing album: $album"

    # Determine the album hash
    if [[ -n "$(curl -sI -- "http://imgur.com/a/$album" | head -n 1 | grep 200)" ]]; then
        album_hash=${album:0:5}
    elif [[ -n "$(curl -sI -- "$album" | head -n 1 | grep 200)" ]]; then
        album_hash=$(echo "$album" | perl -ne 'm/imgur.com\/a\/(\w{5})/; print $1')
    else
        echo "error: could not read album: $album" >&2
        continue
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
        continue
    fi

    # Extract the image hashes and extensions
    images=$(curl -s "$album_url" | tr '}' '\n' | perl -ne 'print "$1$2\n" if m/"hash":"(.{5})".+"ext":"(\..{3,4})"/')

    # Download and store the images concurrently
    for image in $images; do
        (
            # Download the image and save it, storing the return code of curl
            verbose && echo "downloading image: $image"
            curl -so "$album_hash/$image" "http://i.imgur.com/$image"
            return_code=$?

            if verbose; then
                if [[ $return_code -eq 0 ]]; then
                    echo "saved image: $image"
                else
                    echo "error: could not download image: $image" >&2
                fi
            fi
        ) &
    done
done

# Wait for all background jobs to finish
wait

# Indicate completion
verbose && echo "done"

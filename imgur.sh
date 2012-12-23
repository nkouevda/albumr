#!/bin/bash

# Nikita Kouevda
# 2012/12/23

# Store script name and directory
SCRIPT_NAME="${0##*/}"
SCRIPT_DIR="${0%/*}"

# Parse the given arguments
PARSED_ARGS=$(getopt v $*)

# Print usage and exit if parsing error
if [[ $? != 0 ]]; then
    echo "Usage: $SCRIPT_NAME [-v] [album ...]"
    exit 1
fi

# Set arguments to parsed arguments
set -- $PARSED_ARGS

# Iterate over options
for ARG in "$@"; do
    case "$ARG" in
        # Enable verbose output
        -v)
            VERBOSE=1
            shift
            ;;
        # End options
        --)
            shift
            break
            ;;
    esac
done

# Iterate over the given albums
for ALBUM in "$@"; do
    # Print the album being processed
    [[ "$VERBOSE" ]] && echo "Processing album: $ALBUM"

    # Determine the album URL and hash
    if [[ -n "$(curl -sI "http://imgur.com/a/$ALBUM" | head -n 1 | grep 200)" ]]; then
        ALBUM_URL="http://imgur.com/a/$ALBUM"
        ALBUM_HASH="$ALBUM"
    elif [[ -n "$(curl -sI "$ALBUM" | head -n 1 | grep 200)" ]]; then
        ALBUM_URL="$ALBUM"
        ALBUM_HASH=$(echo "$ALBUM" | perl -ne 'm/imgur.com\/a\/(\w{5})/; print $1')
    else
        echo "Error: could not read album: $ALBUM" >&2
        continue
    fi

    # Print the album URL and hash
    [[ "$VERBOSE" ]] && echo "Album URL: $ALBUM_URL"
    [[ "$VERBOSE" ]] && echo "Album hash: $ALBUM_HASH"

    # Use the album hash to make the directory if necessary
    if [[ ! -e "$ALBUM_HASH" ]]; then
        [[ "$VERBOSE" ]] && echo "Making directory: $ALBUM_HASH"
        mkdir "$ALBUM_HASH"
    elif [[ ! -d "$ALBUM_HASH" ]]; then
        echo "Error: not a directory: $ALBUM_HASH" >&2
        continue
    fi

    # Extract the image hashes and extensions
    IMAGES=$(curl -s "$ALBUM_URL" | tr '}' '\n' | perl -ne 'print "$1$2\n" if m/"hash":"(.{5})".+"ext":"(\..{3,4})"/')

    # Download and store the images concurrently
    for IMAGE in $IMAGES; do
        (
            curl -so "$ALBUM_HASH/$IMAGE" "http://i.imgur.com/$IMAGE"
            ERROR_CODE=$?

            if [[ "$VERBOSE" ]]; then
                if [[ $ERROR_CODE == 0 ]]; then
                    echo "Saved image: $IMAGE"
                else
                    echo "Error: could not download image: $IMAGE" >&2
                fi
            fi
        ) &
    done
done

# Wait for all background jobs to finish
wait

# Indicate completion
[[ "$VERBOSE" ]] && echo "Done"

#!/bin/bash

# Nikita Kouevda
# 2012/12/22

# Iterate over the given albums
for ALBUM in "$@"; do
    # Establish the album url and hash
    if [ -n "`curl -sI "http://imgur.com/a/$ALBUM" | head -n 1 | grep 200`" ]; then
        ALBUM_URL="http://imgur.com/a/$ALBUM"
        ALBUM_HASH="$ALBUM"
    elif [ -n "`curl -sI "$ALBUM" | head -n 1 | grep 200`" ]; then
        ALBUM_URL="$ALBUM"
        ALBUM_HASH=$(echo "$ALBUM" | perl -ne 'm/imgur.com\/a\/(\w{5})/; print $1')
    else
        echo "error: could not read album: $ALBUM" >&2
        continue
    fi

    # Use the album hash to make the directory if necessary
    mkdir -p "$ALBUM_HASH"

    # Extract the image hashes and extensions
    IMAGES=$(curl -s "$ALBUM_URL" | tr '}' '\n' | perl -ne 'print "$1$2\n" if m/"hash":"(.{5})".+"ext":"(\..{3,4})"/')

    # Download and store the images concurrently
    for IMAGE in "$IMAGES"; do
        curl -so "$ALBUM_HASH/$IMAGE" "http://i.imgur.com/$IMAGE" &
    done
done

# Wait for all background jobs to finish
wait

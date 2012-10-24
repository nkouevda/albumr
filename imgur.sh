#!/bin/bash

# Nikita Kouevda
# 2012/10/23

# Iterate over the given album hashes
for ALBUM in $@; do
    # Skip this iteration if the album could not be read
    if [ -z "`curl -sI http://imgur.com/a/$ALBUM | head -n 1 | grep 200`" ]; then
        echo "error: could not read album: $ALBUM" >&2
        continue
    fi

    # Make the directory if necessary
    mkdir -p $ALBUM

    # Extract image hashes and extensions
    IMAGES=$(curl -s http://imgur.com/a/$ALBUM | tr '}' '\n' | perl -ne 'print "$1$2\n" if m/"hash":"(.{5})".+"ext":"(\..{3,4})"/')

    # Download and store the images concurrently
    for IMAGE in "$IMAGES"; do
        curl -so "$ALBUM/$IMAGE" "http://i.imgur.com/$IMAGE" &
    done
done

# Wait for completion
wait

#!/bin/bash

if [[ -n "$1" ]]; then
    export $(cat ../.env.$1 | xargs)
else
    export $(cat ../.env | xargs)
fi

npm run build && cp -r ./dist/* ../static

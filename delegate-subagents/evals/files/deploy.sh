#!/usr/bin/env bash
set -eu
target="${1:?usage: deploy.sh <staging|production>}"
rsync -az --delete dist/ "deploy@$target.example.internal:/srv/app/"
ssh "deploy@$target.example.internal" 'sudo systemctl restart app'
echo "deployed to $target"

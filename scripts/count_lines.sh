#!/usr/bin/env bash

ROOT="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")"

cd ${ROOT}
echo -e "\nTests: "
echo "$(wc -l tests/*.py)"
echo -e "\nScripts: "
echo "$(wc -l scripts/*)"
echo -e "\nTemplates: "
echo "$(wc -l tuir/templates/*)"
echo -e "\nCode: "
echo "$(wc -l tuir/*.py)"
echo -e "\nCombined: "
echo "$(cat tests/*.py scripts/* tuir/templates/* tuir/*.py | wc -l) total lines"

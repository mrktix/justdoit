#!/bin/sh

grep "//jdi-$1" $2 | awk -F '//==' '{print $2}' | head -n 1

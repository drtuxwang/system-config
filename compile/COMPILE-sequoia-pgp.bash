#!/usr/bin/env bash

cd ${0%/*}
umask 022

export RUST_BACKTRACE=1

cargo build --release --locked --no-default-features --features crypto-openssl

ls -l $PWD/target/release/sq
strip $PWD/target/release/sq 2> /dev/null
ls -l $PWD/target/release/sq
fmod -R $PWD/install 2> /dev/null

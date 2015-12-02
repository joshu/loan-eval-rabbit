#! /usr/bin/bash

cd aggregator
docker build -t fre/aggregator .
cd ../credit
docker build -t fre/credit .
cd ../eval
docker build -t fre/eval .
cd ../gateway
docker build -t fre/gateway .
cd ../purchase
docker build -t fre/purchase .
cd ../validate
docker build -t fre/validate .
cd ..

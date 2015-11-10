#! /usr/local/bin/bash
cd aggregator
docker run -d -e RABBIT_ADDR='172.17.0.2' --name aggregator fre/aggregator
cd ../credit
docker run -d -e RABBIT_ADDR='172.17.0.2' --name credit fre/credit
cd ../gateway
docker run -d -e RABBIT_ADDR='172.17.0.2' --name gateway fre/gateway
cd ../purchase
docker run -d -e RABBIT_ADDR='172.17.0.2' --name purchase fre/purchase
cd ../validate
docker run -d -e RABBIT_ADDR='172.17.0.2' --name validate fre/validate
cd ..
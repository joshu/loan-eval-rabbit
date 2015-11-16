#! /usr/local/bin/bash
docker run -d -e RABBIT_ADDR='172.17.0.2' --name aggregator fre/aggregator
docker run -d -e RABBIT_ADDR='172.17.0.2' --name credit fre/credit
docker run -d -e RABBIT_ADDR='172.17.0.2' --name gateway fre/gateway
docker run -d -e RABBIT_ADDR='172.17.0.2' --name purchase fre/purchase
docker run -d -e RABBIT_ADDR='172.17.0.2' --name validate fre/validate
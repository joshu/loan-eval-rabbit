#! /usr/local/bin/bash
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="aggregator" --name aggregator fre/aggregator
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="credit" --name credit fre/credit
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="eval" --name eval fre/eval
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="rest_gateway" -p 6080:6080 --name rest_gateway fre/rest_gateway
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="purchase" --name purchase fre/purchase
docker run -d -e RABBIT_ADDR='172.17.0.2' -e COLLECTD_DOCKER_APP="loan_eval" -e COLLECTD_DOCKER_TASK="validate" --name validate fre/validate
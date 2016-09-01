#!/bin/sh
set -x
set -e

DIR=$(dirname $(readlink -f $0))/ssl

for f in ca agent master; do
	openssl genrsa -out $DIR/$f.key 1024
done

# generate the CA certificate first - note that CN has to be different from the
# master and agent CN!
openssl req -x509 -new -nodes -sha256 -days 365 -subj "/CN=prove.localhost" \
	-key $DIR/ca.key -out $DIR/ca.crt

# generate CSR and then a certificate for master and agent. note that these only
# work for localhost, if you want to run in vagrant or on separate servers
# you'll have to tweak the CN
for f in agent master; do
	openssl req -new -sha256 -subj "/CN=localhost" -days 365 \
		-key $DIR/$f.key -out $DIR/$f.csr
	openssl x509 -req -days 365 -sha256 -CAcreateserial \
		-CA $DIR/ca.crt -CAkey $DIR/ca.key \
		-in $DIR/$f.csr -out $DIR/$f.crt
done

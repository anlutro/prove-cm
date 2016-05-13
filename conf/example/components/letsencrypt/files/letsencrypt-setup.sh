#!/bin/sh

cert_name=$1 && shift

subj=''
for domain in "$@"; do
	[ -z $subj ] || subj="${subj},"
	subj="${subj}DNS:${domain}"
done

openssl req -new -sha256 -key /etc/letsencrypt/domains/$cert_name.key -subj "/" -reqexts SAN \
	-config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=$subj")) \
	> /etc/letsencrypt/domains/$cert_name.csr

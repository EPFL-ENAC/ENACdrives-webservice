
FROM httpd:2.4

# Tequila
RUN apt -qy update; \
    apt -qy install wget build-essential ca-certificates \
    apache2-dev libssl-dev libc-client-dev libkrb5-dev libpq-dev

RUN cd / && wget https://tequila.epfl.ch/download/2.0/tequila-apache-C-2.0.17.tgz
RUN cd / && tar zxvf tequila-apache-C-2.0.17.tgz
RUN cd /tequila-2.0.17/Apache/C/ && make && apxs -c -i -DAPACHE2 -DUSESSL -lssl mod_tequila.c

COPY httpd.conf /usr/local/apache2/conf/httpd.conf

RUN mkdir /var/tequila \
    && chown www-data: /var/tequila \
    && mkdir -p /var/log/apache2 \
    && chown www-data: /var/log/apache2

EXPOSE 80

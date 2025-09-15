
FROM httpd:2.4-trixie

RUN apt-get -qy update \
    && apt-get -qy install wget

RUN cd / \
    && wget https://github.com/OpenIDC/mod_auth_openidc/releases/download/v2.4.18/libapache2-mod-auth-openidc_2.4.18-1.trixie_amd64.deb \
    && apt-get -qy install ./libapache2-mod-auth-openidc_2.4.18-1.trixie_amd64.deb

EXPOSE 80

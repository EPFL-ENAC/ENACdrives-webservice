
FROM httpd:2.4

RUN apt-get -qy update \
    && apt-get -qy install wget

RUN cd / \
    && wget https://github.com/OpenIDC/mod_auth_openidc/releases/download/v2.4.16.8/libapache2-mod-auth-openidc_2.4.16.8-1.bookworm_amd64.deb \
    && apt-get -qy install ./libapache2-mod-auth-openidc_2.4.16.8-1.bookworm_amd64.deb

EXPOSE 80

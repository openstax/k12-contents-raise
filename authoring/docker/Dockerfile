
FROM moodlehq/moodle-php-apache:8.0 as base

ARG MOODLE_VERSION=v4.0.2
ARG LOCAL_CODECHECKER_VERSION=v3.1.0
ARG LOCAL_MOODLECHECK_VERSION=v1.0.9
ARG TOOL_PLUGINSKEL_VERSION=1.5.3
ARG LOCAL_RAISECLI_VERSION=2022021400

# Install Moodle and plugins
RUN rmdir /var/www/html
RUN git clone --depth 1 https://github.com/moodle/moodle --branch $MOODLE_VERSION /var/www/html
RUN find /var/www/html/. -name .git | xargs rm -rf
RUN chown -R www-data:www-data /var/www/html/

RUN apt-get update && apt-get install -y cron

COPY authoring/docker/moodle-config.php /var/www/html/config.php
COPY authoring/docker/php.ini-development /usr/local/etc/php/php.ini
COPY authoring/docker/cron.moodle /etc/cron.d/moodle
RUN chmod 644 /etc/cron.d/moodle

FROM base as dbg

RUN pecl update-channels && pecl install xdebug
COPY moodle/docker-php-ext-xdebug.ini /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
RUN docker-php-ext-enable xdebug

FROM base as dev
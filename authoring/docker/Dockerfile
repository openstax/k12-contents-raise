
FROM moodlehq/moodle-php-apache:8.0 as base

ARG MOODLE_VERSION=v4.0.2
ARG LOCAL_CODECHECKER_VERSION=v3.1.0
ARG LOCAL_MOODLECHECK_VERSION=v1.0.9
ARG TOOL_PLUGINSKEL_VERSION=1.5.3
ARG LOCAL_RAISECLI_VERSION=2022021400

# Install Moodle and plugins
RUN rmdir /var/www/html
RUN git clone --depth 1 https://github.com/moodle/moodle --branch $MOODLE_VERSION /var/www/html
RUN git clone --depth 1 https://github.com/moodlehq/moodle-local_codechecker.git --branch $LOCAL_CODECHECKER_VERSION /var/www/html/local/codechecker
RUN git clone --depth 1 https://github.com/moodlehq/moodle-local_moodlecheck.git --branch $LOCAL_MOODLECHECK_VERSION /var/www/html/local/moodlecheck
RUN git clone --depth 1 https://github.com/mudrd8mz/moodle-tool_pluginskel.git --branch $TOOL_PLUGINSKEL_VERSION /var/www/html/admin/tool/pluginskel
RUN git clone --depth 1 https://github.com/openstax/moodle-local_raisecli.git --branch $LOCAL_RAISECLI_VERSION /var/www/html/local/raisecli
RUN find /var/www/html/. -name .git | xargs rm -rf
RUN chown -R www-data:www-data /var/www/html/

RUN apt-get update && apt-get install -y cron

COPY moodle/moodle-config.php /var/www/html/config.php
COPY moodle/php.ini-development /usr/local/etc/php/php.ini
COPY moodle/cron.moodle /etc/cron.d/moodle
RUN chmod 644 /etc/cron.d/moodle

FROM base as dbg

RUN pecl update-channels && pecl install xdebug
COPY moodle/docker-php-ext-xdebug.ini /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
RUN docker-php-ext-enable xdebug

FROM base as dev
FROM moodlehq/moodle-php-apache:8.0

ARG MOODLE_VERSION=v4.0.2

# Install Moodle and plugins
RUN rmdir /var/www/html
RUN git clone --depth 1 https://github.com/moodle/moodle --branch $MOODLE_VERSION /var/www/html
RUN find /var/www/html/. -name .git | xargs rm -rf
RUN chown -R www-data:www-data /var/www/html/

RUN apt-get update && apt-get install -y cron

COPY moodle-config.php /var/www/html/config.php
COPY php.ini-development /usr/local/etc/php/php.ini
COPY cron.moodle /etc/cron.d/moodle
COPY wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh
RUN chmod 644 /etc/cron.d/moodle

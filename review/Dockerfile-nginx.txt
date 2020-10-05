FROM nginx:1.19.2

WORKDIR /static

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d

RUN chown -R nginx:nginx /static

WORKDIR /media
RUN chown -R nginx:nginx /media
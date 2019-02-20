FROM docker.io/openshift/base-centos7

USER root

COPY requirements.txt language_api.py ${HOME}/

RUN curl https://bootstrap.pypa.io/get-pip.py | python && \
    pip install --no-cache --upgrade -r ${HOME}/requirements.txt

EXPOSE 8080

# ELASTICACHE= LANGUAGELAYER_API_KEY= ./language_api.py
CMD ["./language_api.py"]


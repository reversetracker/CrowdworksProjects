ARG elasticsearch_version=8.5.1

FROM docker.elastic.co/elasticsearch/elasticsearch:${elasticsearch_version}

RUN bin/elasticsearch-plugin install analysis-nori

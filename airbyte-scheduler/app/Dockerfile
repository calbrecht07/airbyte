ARG JDK_VERSION=17.0.1
FROM openjdk:${JDK_VERSION}-slim AS scheduler

ARG VERSION=0.36.2-alpha

ENV APPLICATION airbyte-scheduler
ENV VERSION ${VERSION}

WORKDIR /app

ADD bin/${APPLICATION}-${VERSION}.tar /app

# wait for upstream dependencies to become available before starting server
ENTRYPOINT ["/bin/bash", "-c", "${APPLICATION}-${VERSION}/bin/${APPLICATION}"]

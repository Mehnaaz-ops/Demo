FROM hub.docker.hpecorp.net/sabuild/jenkins-slave:java11-base-2023-03-09


ADD common/scripts/docker-client.sh \
     common/scripts/kubectl-helm.sh /common/scripts/


# Install kubectl,helm and docker-client 
RUN /common/scripts/kubectl-helm.sh && \
    /common/scripts/docker-client.sh

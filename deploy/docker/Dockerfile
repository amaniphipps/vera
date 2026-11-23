# Vera on Hermes Agent - all-in-one image.
#
# Build:  docker build -f deploy/docker/Dockerfile -t vera .
# Run:    docker run -d --env-file .env -v vera-data:/opt/data vera
#
# The base image is the official Hermes runtime. This layer adds Vera:
# her skills, persona, policy, and knowledge seed - seeded into the /opt/data
# volume on first boot by the entrypoint (so the volume stays yours after that).

FROM nousresearch/hermes-agent:latest

WORKDIR /opt/vera
COPY skills ./skills
COPY personas ./personas
COPY policy ./policy
COPY knowledge ./knowledge
COPY capability ./capability
COPY setup ./setup
COPY docs ./docs
COPY .env.example ./.env.example

ENV PATH="/root/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && uv tool install --python 3.12 "graphifyy[mcp]" || true

ENV HERMES_HOME=/opt/data

COPY deploy/docker/entrypoint.sh /opt/vera/entrypoint.sh
RUN chmod +x /opt/vera/entrypoint.sh

ENTRYPOINT ["/opt/vera/entrypoint.sh"]
CMD ["gateway", "run"]

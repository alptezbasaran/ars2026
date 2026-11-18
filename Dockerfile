# Quarto, for previewing and rendering the deck.
#
# Builds natively on amd64 and arm64. The official ghcr.io/quarto-dev/quarto
# image is published for amd64 only (on Apple silicon it runs under
# emulation), so this installs the Quarto release package that matches the
# build platform instead. Keep QUARTO_VERSION equal to the version in
# .github/workflows/deploy-page.yml, so a local render and the published site
# come from the same Quarto.
FROM ubuntu:22.04

ARG QUARTO_VERSION=1.6.40
ARG TARGETARCH

RUN set -eu; \
    arch="${TARGETARCH:-$(dpkg --print-architecture)}"; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl; \
    curl -fsSL -o /tmp/quarto.deb \
      "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${arch}.deb"; \
    dpkg -i /tmp/quarto.deb; \
    rm /tmp/quarto.deb; \
    apt-get purge -y curl; \
    apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /project
EXPOSE 4000
CMD ["quarto", "--version"]

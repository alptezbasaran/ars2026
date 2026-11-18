# Python toolchain for the figure scripts (matplotlib, numpy, pandas, Pillow,
# segno for the QR code) and the deck QA suite (Playwright; zxing-cpp decodes
# the QR code back to check it). The Playwright image carries the browsers
# and their system libraries for both amd64 and arm64, but not the Python
# package; it is installed at the same version, so it finds those browsers.
ARG PLAYWRIGHT_VERSION=1.55.0
FROM mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble
ARG PLAYWRIGHT_VERSION

RUN pip install --no-cache-dir --break-system-packages --root-user-action=ignore \
      "playwright==${PLAYWRIGHT_VERSION}" \
      matplotlib==3.11.2 numpy==2.5.3 pandas==3.0.6 pillow==12.3.0 \
      segno==1.6.6 zxing-cpp==3.1.1

# The QA scripts default to the installed Google Chrome; inside the container
# they use the bundled Chromium, since Google Chrome has no Linux arm64 build.
ENV QA_BROWSER_CHANNEL="" \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /work

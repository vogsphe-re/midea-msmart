# Build step
FROM python:3.11-alpine as build
ARG TARGETPLATFORM
RUN apk add --update git
RUN pip install build
WORKDIR /msmart-build
COPY . .
RUN python -m build
# pycryptodome doesn't ship armv7 wheels, so build one manually
RUN if [ "$TARGETPLATFORM" == "linux/arm/v7" ]; then \
      apk add --update build-base; \
      pip wheel pycryptodome; \
    fi

# Production step
FROM python:3.11-alpine
ARG TARGETPLATFORM
COPY --from=build /msmart-build/dist/msmart_ng-*.whl /msmart-build/pycryptodome-*.whl /tmp
# Install pre-built pycryptodome wheel from build image
RUN if [ "$TARGETPLATFORM" == "linux/arm/v7" ]; then \
      pip install /tmp/pycryptodome-*.whl; \
    fi
RUN pip install /tmp/msmart_ng-*.whl
ENTRYPOINT ["/usr/local/bin/midea-discover"]

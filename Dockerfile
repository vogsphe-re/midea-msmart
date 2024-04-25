# Build step
FROM python:3.11-alpine as build
RUN apk add --update git
RUN pip install build
WORKDIR /msmartvog-build
COPY . .
RUN python -m build

# Production step
# Using base alpine package so we can utilize pycryptodome in package repo
FROM alpine:3.18
RUN apk add --update python3 py3-pip py3-pycryptodome
COPY --from=build /msmartvog-build/dist/msmartvog-*.whl /tmp
RUN pip install /tmp/msmartvog-*.whl
ENTRYPOINT ["/usr/bin/msmartvog"]

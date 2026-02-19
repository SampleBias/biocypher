# Bi0cyph3r Backend - Multi-stage build
# Build stage
FROM rust:1.75-bookworm AS build
WORKDIR /build

# Copy workspace files
COPY Cargo.toml Cargo.lock ./
COPY backend ./backend
COPY static ./static

# Build release binary
RUN cargo build --release --bin biocypher-backend

# Runtime stage
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Preserve path structure: binary expects CARGO_MANIFEST_DIR/../static
# At build time: /build/backend/../static = /build/static
COPY --from=build /build/static /build/static
COPY --from=build /build/target/release/biocypher-backend /usr/local/bin/

EXPOSE 8080

# Bind to 0.0.0.0 for container access
ENV BIND_ADDRESS=0.0.0.0:8080

CMD ["biocypher-backend"]

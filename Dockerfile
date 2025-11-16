FROM node:19.0.1 as builder-frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM rust:1.90.0 as builder-backend
WORKDIR /usr/src/app
COPY . .
RUN cargo install --locked --path .

FROM debian:bookworm-slim
COPY --from=builder-backend /usr/local/cargo/bin/serien-and-movie-planer /usr/local/bin/serien-and-movie-planer
COPY --from=builder-frontend /build/build /frontend/build
CMD ["serien-and-movie-planer"]

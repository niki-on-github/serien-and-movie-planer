mod handlers;
mod routes;

use actix_web::{middleware, web, App, HttpResponse, HttpServer};

static DEFAULT_HOST: &str = "0.0.0.0";
const DEFAULT_PORT: u16 = 8888;
static DEFAULT_RUST_LOG: &str = "actix_web=info";

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let rust_log = std::env::var("RUST_LOG").unwrap_or(DEFAULT_RUST_LOG.to_string());
    std::env::set_var("RUST_LOG", rust_log);
    env_logger::init();

    let port: u16 = std::env::var("PORT").unwrap_or(DEFAULT_PORT.to_string()).parse::<u16>().unwrap_or(DEFAULT_PORT);
    let host = std::env::var("HOST").unwrap_or(DEFAULT_HOST.to_string());

    println!("Start Server {}:{}", host, port);
    HttpServer::new(|| {
        App::new()
            .wrap(middleware::Logger::default())
            .default_service(web::route().to(HttpResponse::NotFound))
            .configure(routes::init)
    })
    .bind((host, port))?
    .run()
    .await
    .ok();

    Ok(())
}

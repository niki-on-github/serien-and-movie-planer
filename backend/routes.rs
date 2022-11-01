use crate::handlers;
use actix_web::web;


pub fn init(cfg: &mut web::ServiceConfig) {
    cfg.service(handlers::get_movies);
    cfg.service(handlers::get_series);
    cfg.service(handlers::index());
}

use crate::handlers;
use actix_web::web;


pub fn init(cfg: &mut web::ServiceConfig) {
    cfg.service(handlers::get_movies);
    cfg.service(handlers::put_movies);
    cfg.service(handlers::get_serien);
    cfg.service(handlers::put_serien);
    cfg.service(handlers::index());
}

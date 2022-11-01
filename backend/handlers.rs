use actix_files::Files;
use actix_web::{get, Responder};
use serde_json::json;
extern crate chrono;

const POSTGRES_USER: &str = "root";
const POSTGRES_PASSWORD: &str = "Geheim";
const POSTGRES_HOST: &str = "localhost";
const POSTGRES_PORT: &str = "5432";
const POSTGRES_DATABASE: &str = "postgres";

pub fn index() -> Files {
    Files::new("/", "./frontend/build/").index_file("index.html")
}


#[get("/v1/movies")]
async fn get_movies() -> impl Responder {
    let connect_uri: String = format!("postgresql://{}:{}@{}:{}/{}", POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE);
    let (client, conn) = match tokio_postgres::connect(connect_uri.as_str().as_ref(), tokio_postgres::NoTls).await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            }).to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut movies: Vec<serde_json::Value> = Vec::new();
    for row in client.query("SELECT ID,TITLE,LONG_TITLE,DATE FROM MOVIES", &[]).await.unwrap_or(Vec::new()) {
        movies.push(json!({
                "id": row.get::<usize, i32>(0),
                "title": row.get::<usize, &str>(1),
                "longTitle": row.get::<usize, &str>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string()
        }));
    }

    json!(movies).to_string()
}

#[get("/v1/serien")]
async fn get_series() -> impl Responder {
    let connect_uri: String = format!("postgresql://{}:{}@{}:{}/{}", POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE);
    let (client, conn) = match tokio_postgres::connect(connect_uri.as_str().as_ref(), tokio_postgres::NoTls).await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            }).to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut serien: Vec<serde_json::Value> = Vec::new();
    for row in client.query("SELECT ID,TITLE,SEASON,DATE,SENDER FROM SERIEN", &[]).await.unwrap_or(Vec::new()) {
        serien.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "sender": row.get::<usize, &str>(4),
        }));
    }

    json!(serien).to_string()
}

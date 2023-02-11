use actix_files::Files;
use actix_web::{get, put, web, HttpResponse, Responder};
use serde_json::json;
extern crate chrono;
use serde::Deserialize;
use serde_json;
use serde_json::Number;
use std::path::Path;

const DEFAULT_POSTGRES_USER: &str = "root";
const DEFAULT_POSTGRES_PASSWORD: &str = "postgres";
const DEFAULT_POSTGRES_HOST: &str = "localhost";
const DEFAULT_POSTGRES_PORT: &str = "5432";
const DEFAULT_POSTGRES_DATABASE: &str = "postgres";

#[derive(Deserialize)]
struct Response {
    key: String,
    values: String,
}

pub fn index() -> Files {
    if Path::new("/frontend/build").exists() {
        Files::new("/", "/frontend/build/").index_file("index.html")
    } else {
        Files::new("/", "./frontend/build/").index_file("index.html")
    }
}

async fn get_postgress_connection() -> Result<
    (
        tokio_postgres::Client,
        tokio_postgres::Connection<tokio_postgres::Socket, tokio_postgres::tls::NoTlsStream>,
    ),
    tokio_postgres::Error,
> {
    let user = std::env::var("POSTGRES_USER").unwrap_or(DEFAULT_POSTGRES_USER.to_string());
    let pw = std::env::var("POSTGRES_PASSWORD").unwrap_or(DEFAULT_POSTGRES_PASSWORD.to_string());
    let host = std::env::var("POSTGRES_HOST").unwrap_or(DEFAULT_POSTGRES_HOST.to_string());
    let port = std::env::var("POSTGRES_PORT").unwrap_or(DEFAULT_POSTGRES_PORT.to_string());
    let db = std::env::var("POSTGRES_DB").unwrap_or(DEFAULT_POSTGRES_DATABASE.to_string());
    let connect_uri: String = format!("postgresql://{}:{}@{}:{}/{}", user, pw, host, port, db);
    tokio_postgres::connect(connect_uri.as_str().as_ref(), tokio_postgres::NoTls).await
}

#[put("/v1/movies/update")]
async fn put_movies(body: web::Form<Response>) -> impl Responder {
    let values_json: serde_json::Value = serde_json::from_str(body.values.as_str()).unwrap();
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(_e) => return HttpResponse::Created().finish(),
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let state: String = match &values_json["state"].clone() {
        serde_json::Value::String(s) => s.to_string(),
        _ => "".to_string(),
    };
    let key = body.key.parse::<i32>().unwrap();

    if !state.is_empty() {
        client
            .execute(
                "UPDATE MOVIES SET STATE = $2 WHERE ID = $1 RETURNING *;",
                &[&key, &state],
            )
            .await
            .unwrap();
    }

    HttpResponse::Created().finish()
}

#[put("/v1/serien/update")]
async fn put_serien(body: web::Form<Response>) -> impl Responder {
    let values_json: serde_json::Value = serde_json::from_str(body.values.as_str()).unwrap();
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(_e) => return HttpResponse::Created().finish(),
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let state: String = match &values_json["state"].clone() {
        serde_json::Value::String(s) => s.to_string(),
        _ => "".to_string(),
    };

    if !state.is_empty() {
        client
            .execute(
                "UPDATE SERIEN SET STATE = $2 WHERE ID = $1 RETURNING *;",
                &[&body.key, &state],
            )
            .await
            .unwrap();
    }

    HttpResponse::Created().finish()
}

#[get("/v1/movies")]
async fn get_movies() -> impl Responder {
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            })
            .to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut movies: Vec<serde_json::Value> = Vec::new();
    for row in client
        .query("SELECT ID,TITLE,LONG_TITLE,DATE,STATE FROM MOVIES", &[])
        .await
        .unwrap_or(Vec::new())
    {
        movies.push(json!({
                "id": row.get::<usize, i32>(0),
                "title": row.get::<usize, &str>(1),
                "longTitle": row.get::<usize, &str>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "state": row.get::<usize, &str>(4),
        }));
    }

    json!(movies).to_string()
}

#[get("/v1/serien")]
async fn get_serien() -> impl Responder {
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            })
            .to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut serien: Vec<serde_json::Value> = Vec::new();
    for row in client
        .query("SELECT ID,TITLE,SEASON,DATE,SENDER,STATE FROM SERIEN", &[])
        .await
        .unwrap_or(Vec::new())
    {
        serien.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "sender": row.get::<usize, &str>(4),
                "state": row.get::<usize, &str>(5),
        }));
    }

    json!(serien).to_string()
}

#[get("/v1/serien/count")]
async fn get_serien_count() -> impl Responder {
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            })
            .to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut map = serde_json::Map::new();
    for row in client
        .query("SELECT STATE,COUNT(STATE) FROM SERIEN GROUP BY STATE", &[])
        .await
        .unwrap_or(Vec::new())
    {
        map.insert(
            row.get::<usize, &str>(0).to_string(),
            serde_json::Value::Number(Number::from(row.get::<usize, i64>(1))),
        );
    }

    json!(map).to_string()
}

#[get("/v1/movies/count")]
async fn get_movies_count() -> impl Responder {
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(e) => {
            return json!({
                "error": e.to_string()
            })
            .to_string();
        }
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    let mut map = serde_json::Map::new();
    for row in client
        .query("SELECT STATE,COUNT(STATE) FROM MOVIES GROUP BY STATE", &[])
        .await
        .unwrap_or(Vec::new())
    {
        map.insert(
            row.get::<usize, &str>(0).to_string(),
            serde_json::Value::Number(Number::from(row.get::<usize, i64>(1))),
        );
    }

    json!(map).to_string()
}

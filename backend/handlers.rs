use actix_files::Files;
use actix_web::{get, post, put, web, HttpResponse, Responder};
use serde_json::json;
extern crate chrono;
use serde::{Deserialize, Serialize};
use serde_json;
use serde_json::Number;
use std::path::Path;
use std::env;

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

#[derive(Deserialize)]
struct AddTrackerResponse {
    value: i32,
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
    let pw_encoded = urlencoding::encode(&pw);
    let host = std::env::var("POSTGRES_HOST").unwrap_or(DEFAULT_POSTGRES_HOST.to_string());
    let port = std::env::var("POSTGRES_PORT").unwrap_or(DEFAULT_POSTGRES_PORT.to_string());
    let db = std::env::var("POSTGRES_DB").unwrap_or(DEFAULT_POSTGRES_DATABASE.to_string());
    let _connect_uri: String = format!(
        "postgresql://{}:{}@{}:{}/{}",
        user, pw_encoded, host, port, db
    );

    tokio_postgres::Config::new()
        .host(&host)
        .user(&user)
        .port(port.parse().unwrap_or(5432))
        .password(&pw)
        .dbname(&db)
        .connect(tokio_postgres::NoTls)
        .await
}

#[put("/api/v1/movies/update")]
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

#[put("/api/v1/serien/update")]
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

#[put("/api/v1/track/update")]
async fn put_track(body: web::Form<Response>) -> impl Responder {
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
                "UPDATE TRACK SET STATE = $2 WHERE ID = $1 RETURNING *;",
                &[&body.key, &state],
            )
            .await
            .unwrap();
    }

    HttpResponse::Created().finish()
}

#[post("/api/v1/track/add")]
async fn post_track(body: web::Json<AddTrackerResponse>) -> impl Responder {
    println!("add {}", body.value);
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(_e) => return HttpResponse::InternalServerError().finish(),
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });


    if body.value != 0 {
        client
            .execute(
                "CREATE TABLE IF NOT EXISTS TRACKID (ID INT PRIMARY KEY NOT NULL);",
                &[],
            )
            .await
            .unwrap();

        client
            .execute(
                "INSERT INTO TRACKID (ID) VALUES($1) ON CONFLICT DO NOTHING;",
                &[&body.value],
            )
            .await
            .unwrap();
    }

    HttpResponse::Created().finish()
}

#[get("/api/v1/movies")]
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

#[get("/api/v1/serien")]
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
        .query("SELECT ID,TITLE,SEASON,DATE,STATE FROM SERIEN", &[])
        .await
        .unwrap_or(Vec::new())
    {
        serien.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "state": row.get::<usize, &str>(4),
        }));
    }

    json!(serien).to_string()
}

#[get("/api/v1/track")]
async fn get_track() -> impl Responder {
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
        .query("SELECT ID,TITLE,SEASON,DATE,STATE FROM TRACK", &[])
        .await
        .unwrap_or(Vec::new())
    {
        serien.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "state": row.get::<usize, &str>(4),
        }));
    }

    json!(serien).to_string()
}

#[get("/api/v1/serien/count")]
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

#[get("/api/v1/movies/count")]
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

#[get("/api/v1/export")]
async fn get_export() -> impl Responder {
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
        .query("SELECT ID,TITLE,SEASON,DATE,STATE FROM SERIEN", &[])
        .await
        .unwrap_or(Vec::new())
    {
        serien.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "state": row.get::<usize, &str>(4),
        }));
    }

    let mut track: Vec<serde_json::Value> = Vec::new();
    for row in client
        .query("SELECT ID,TITLE,SEASON,DATE,STATE FROM TRACK", &[])
        .await
        .unwrap_or(Vec::new())
    {
        track.push(json!({
                "id": row.get::<usize, &str>(0),
                "title": row.get::<usize, &str>(1),
                "season": row.get::<usize, i32>(2),
                "date": row.get::<usize, chrono::NaiveDate>(3).format("%Y-%m-%d").to_string(),
                "state": row.get::<usize, &str>(4),
        }));
    }

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

    let mut track_ids: Vec<i32> = Vec::new();
    for row in client
        .query("SELECT ID FROM TRACKID", &[])
        .await
        .unwrap_or(Vec::new())
    {
        track_ids.push(row.get::<usize, i32>(0));
    }

    json!({
        "serien": serien,
        "movies": movies,
        "track": track,
        "trackIds": track_ids
    })
    .to_string()
}

#[derive(Serialize, Deserialize)]
pub struct ImportDto {
    pub serien: Vec<serde_json::Value>,
    pub movies: Vec<serde_json::Value>,
    pub track: Vec<serde_json::Value>,
}

#[post("/api/v1/import")]
async fn post_import(body: web::Json<ImportDto>) -> impl Responder {
    let (client, conn) = match get_postgress_connection().await {
        Ok(c) => c,
        Err(_e) => return HttpResponse::Created().finish(),
    };

    tokio::spawn(async move {
        if let Err(e) = conn.await {
            panic!("{}", e.to_string());
        }
    });

    client.execute("DELETE FROM SERIEN;", &[]).await.unwrap();
    
    client.execute("DELETE FROM TRACK;", &[]).await.unwrap();

    client.execute("DELETE FROM MOVIES;", &[]).await.unwrap();

    for s in &body.serien {
        client
            .execute(
                "INSERT INTO SERIEN (ID,TITLE,SEASON,DATE,STATE) VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING;",
                &[&serde_json::from_value::<String>(s["id"].clone()).unwrap(), 
                    &serde_json::from_value::<String>(s["title"].clone()).unwrap(), 
                    &serde_json::from_value::<i32>(s["season"].clone()).unwrap(),
                    &chrono::NaiveDate::parse_from_str(&serde_json::from_value::<String>(s["date"].clone()).unwrap(), "%Y-%m-%d").unwrap(), 
                    &serde_json::from_value::<String>(s["state"].clone()).unwrap()
                ],
            )
            .await
            .unwrap();
    }

    for s in &body.track {
        client
            .execute(
                "INSERT INTO TRACK (ID,TITLE,SEASON,DATE,STATE) VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING;",
                &[&serde_json::from_value::<String>(s["id"].clone()).unwrap(), 
                    &serde_json::from_value::<String>(s["title"].clone()).unwrap(), 
                    &serde_json::from_value::<i32>(s["season"].clone()).unwrap(),
                    &chrono::NaiveDate::parse_from_str(&serde_json::from_value::<String>(s["date"].clone()).unwrap(), "%Y-%m-%d").unwrap(), 
                    &serde_json::from_value::<String>(s["state"].clone()).unwrap()
                ],
            )
            .await
            .unwrap();
    }

    for m in &body.movies {
        client
            .execute(
                "INSERT INTO MOVIES (ID,TITLE,LONG_TITLE,DATE,STATE) VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING;",
                &[&serde_json::from_value::<i32>(m["id"].clone()).unwrap(), 
                    &serde_json::from_value::<String>(m["title"].clone()).unwrap(), 
                    &serde_json::from_value::<String>(m["longTitle"].clone()).unwrap(),
                    &chrono::NaiveDate::parse_from_str(&serde_json::from_value::<String>(m["date"].clone()).unwrap(), "%Y-%m-%d").unwrap(), 
                    &serde_json::from_value::<String>(m["state"].clone()).unwrap()
                ],
            )
            .await
            .unwrap();
    }

    HttpResponse::Created().finish()
}

#[get("/api/v1/trailer/url")]
async fn get_search_url() -> impl Responder {
    env::var("TRAILER_SEARCH_URL").unwrap_or("https://www.youtube.com/results?search_query=".into())
}

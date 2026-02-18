//! Bi0cyph3r Rust Backend Server
//!
//! Main entry point for the Bi0cyph3r DNA cryptography backend service

use actix_cors::Cors;
use actix_web::{middleware, web, App, HttpServer, HttpResponse, Responder};
use tracing::{info, level_filters::LevelFilter};
use tracing_subscriber;

use biocypher_backend::{api, arcium};

/// Health check endpoint
async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "service": "biocypher-backend",
        "version": env!("CARGO_PKG_VERSION")
    }))
}

/// Root endpoint
async fn root() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "name": "Bi0cyph3r Backend API",
        "version": env!("CARGO_PKG_VERSION"),
        "endpoints": {
            "health": "/health",
            "encode": "/api/encode",
            "decode": "/api/decode",
            "safety_screen": "/api/safety-screen",
            "arcium_info": "/api/arcium-info"
        }
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_max_level(LevelFilter::INFO)
        .with_target(false)
        .init();

    info!("🧬 Starting Bi0cyph3r Backend Server v{}", env!("CARGO_PKG_VERSION"));

    // Bind to address from env or default
    let bind_address = std::env::var("BIND_ADDRESS")
        .unwrap_or_else(|_| "127.0.0.1:8080".to_string());

    info!("🚀 Server listening on http://{}", bind_address);

    HttpServer::new(|| {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            // Middleware
            .wrap(cors)
            .wrap(middleware::Logger::default())
            .wrap(middleware::Compress::default())
            .wrap(
                middleware::DefaultHeaders::new()
                    .add(("X-Content-Type-Options", "nosniff"))
                    .add(("X-Frame-Options", "DENY"))
                    .add(("X-XSS-Protection", "1; mode=block"))
            )

            // Routes
            .route("/", web::get().to(root))
            .route("/health", web::get().to(health_check))
            .route("/api/encode", web::post().to(api::encode::encode_message))
            .route("/api/decode", web::post().to(api::decode::decode_message))
            .route("/api/safety-screen", web::post().to(api::safety::safety_screen))
            .route("/api/arcium-info", web::get().to(arcium::arcium_info))
            .service(
                actix_files::Files::new("/app", concat!(env!("CARGO_MANIFEST_DIR"), "/../static"))
                    .index_file("index.html"),
            )
    })
    .bind(&bind_address)?
    .run()
    .await
}

mod crawler;
mod rss;
mod utils;
mod bbc_rss;
mod npr_rss;
mod pbs_rss;
mod ai_jazeera_rss;
mod dw_rss;
mod ap_crawler;

#[tokio::main]
async fn main() {
    utils::setup_logger().expect("Failed to setup logger");
    //let _ = ap_crawler::ap_crawler().await;
    let _ = bbc_rss::bbc_rss().await;
    let _ = npr_rss::npr_rss().await;
    let _ = ai_jazeera_rss::ai_jazeera_rss().await;
    let _ = dw_rss::dw_rss().await;

}

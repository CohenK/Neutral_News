mod crawler;
mod rss;
mod utils;
mod bbc_rss;
mod npr_rss;
mod pbs_rss;
mod ai_jazeera_rss;
mod dw_rss;
mod bloomberg_rss;
mod ap_crawler;

#[tokio::main]
async fn main() {
    utils::setup_logger().expect("Failed to setup logger");
    //let _ = ap_crawler::ap_crawler().await;
    //let _ = bbc_rss::bbc_rss().await;
    //let _ = npr_rss::npr_rss().await;
    //let _ = ai_jazeera_rss::ai_jazeera_rss().await;
    //let _ = dw_rss::dw_rss().await;
    let _ = bloomberg_rss::bloomberg_rss().await;


    // utils::is_valid_article_link(&"https://news.google.com/rss/articles/CBMixgFBVV95cUxOQ0hkR2tuQ3JDT01oUEFfTjd6UDNPd211a00tQnVvVzM0U1N2VHgtbTduWTczTGxEWG1ma0lyeVJkZXFJVWRLZ2FOV0hGSExyQ0FPVVFnQXZZb1B0am8zdlR3ZHI4SEdjLUJvbFJkRDRTbXVRNFhHNnBsYzBHVmNTeWNuRmh6VGwwWmY5eWo5T0dEYVlZRmNLNUt1ZE80YjM4Sm53VVJRa295M2VzdlJpcDNSU2RuTzdDX21VRGhyc2tiOHBDSkE?oc=5".to_string(),
    //  &[].to_vec());
}

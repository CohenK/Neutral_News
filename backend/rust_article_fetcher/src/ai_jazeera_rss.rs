use crate::rss;
use crate::utils;

pub async fn ai_jazeera_rss(){
    let links: Vec<&str> = [
        "https://www.aljazeera.com/xml/rss/all.xml",
        ].to_vec();
    let ignore = ["/videos/", "/program/"].to_vec();
    log::info!("AI Jazeera RSS started.");

    rss::rss(utils::to_vec_string(links), utils::to_vec_string(ignore)).await;
}
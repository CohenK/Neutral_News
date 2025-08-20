use crate::rss;
use crate::utils;

pub async fn bbc_rss(){
    let links: Vec<&str> = [
        "https://feeds.bbci.co.uk/news/rss.xml"
        ].to_vec();
    let ignore = ["iplayer","sounds","videos"].to_vec();
    log::info!("BBC RSS started.");

    rss::rss(utils::to_vec_string(links), utils::to_vec_string(ignore)).await;
}
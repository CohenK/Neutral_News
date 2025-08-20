use crate::rss;
use crate::utils;

pub async fn npr_rss(){
    let links: Vec<&str> = [
        "https://feeds.npr.org/1001/rss.xml"
        ].to_vec();
    let ignore = [].to_vec();
    log::info!("NPR started.");

    rss::rss(utils::to_vec_string(links), utils::to_vec_string(ignore)).await;
}
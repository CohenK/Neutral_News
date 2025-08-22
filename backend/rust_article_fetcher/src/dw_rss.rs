use crate::rss;
use crate::utils;

pub async fn dw_rss(){
    let links: Vec<&str> = [
        "https://rss.dw.com/rdf/rss-en-top",
        "https://rss.dw.com/rdf/rss-en-bus",
        "https://rss.dw.com/xml/rss-en-science",
        "https://rss.dw.com/rdf/rss-en-cul",
        ].to_vec();
    let ignore = [].to_vec();
    log::info!("DW RSS started.");

    rss::rss(utils::to_vec_string(links), utils::to_vec_string(ignore)).await;
}
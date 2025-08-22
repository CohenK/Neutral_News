use crate::rss;
use crate::utils;

pub async fn pbs_rss(){
    let links: Vec<&str> = [
        "https://www.pbs.org/newshour/feeds/rss/headlines",
        "https://www.pbs.org/newshour/feeds/rss/politics",
        "https://www.pbs.org/newshour/feeds/rss/economy",
        "https://www.pbs.org/newshour/feeds/rss/science"
        ].to_vec();
    let ignore = [].to_vec();
    log::info!("PBS RSS started.");

    rss::rss(utils::to_vec_string(links), utils::to_vec_string(ignore)).await;
}
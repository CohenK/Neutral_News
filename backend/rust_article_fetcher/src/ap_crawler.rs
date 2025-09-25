use crate::crawler;

pub async fn ap_crawler(){
    let start_urls = ["https://apnews.com/hub/ap-top-news"];
    let _ = crawler::start_crawl(&start_urls).await;
}



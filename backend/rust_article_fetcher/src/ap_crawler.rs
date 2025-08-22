use crate::crawler;

pub async fn ap_crawler(){
    let ignore = ["ap-fact-check".to_string()].to_vec();
    let start_urls = ["https://apnews.com/"];
    crawler::start_crawl(&start_urls,ignore);
}



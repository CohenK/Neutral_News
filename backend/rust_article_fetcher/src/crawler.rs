use reqwest::Client;
use url::{Url};
use robotstxt::{DefaultMatcher};
use futures::stream::{FuturesUnordered, StreamExt};
use tokio::sync:: {Semaphore};
use std::sync::Arc;
use crate::utils;
struct Crawler {
    //base_urls: Vec<Url>,
    to_visit: Vec<String>,
    client: Client,
    robots_txt: String,
}

impl Crawler {
    async fn new(start_urls: &[&str]) -> Result<Self, Box<dyn std::error::Error>> {
        //let mut base_urls = Vec::new();
        let mut to_visit = Vec::new();
        let client = Client::builder().timeout(std::time::Duration::from_secs(10)).build()?;

        //fetch robots.txt using first link
        let first_url = Url::parse(start_urls[0])?;
        let robots_url = first_url.join("/robots.txt")?;
        let robots_txt = client.get(robots_url).send().await?.text().await?; 

        //seed the crawler with provided URLs
        for &url in start_urls {
            //let parsed = Url::parse(url)?;
            //base_urls.push(parsed);
            let targets = utils::extract_article_links(&client, url).await;
            targets.iter().for_each(|t|to_visit.push(t.to_string()));
        }

        Ok(Crawler {
            //base_urls,
            to_visit,
            client,
            robots_txt
        })
    }

    fn can_fetch(&self, url: &str) -> bool {
        let mut matcher = DefaultMatcher::default();
        matcher.one_agent_allowed_by_robots("*", url, &self.robots_txt)
    }
    
    async fn crawl(&mut self) {
        // concurrently crawl links in to_visit
        let concurrency_limit = 10;
        let semaphore = Arc::new(Semaphore::new(concurrency_limit));
        let mut tasks: FuturesUnordered<tokio::task::JoinHandle<()>> = FuturesUnordered::new();

        // keep crawling if there are links left in to_visit
        while let Some(url) = self.to_visit.pop() {
            if !self.can_fetch(&url) {
                continue;
            }

            let permit = semaphore.clone().acquire_owned().await.unwrap();
            let client = self.client.clone();
            let url_clone = url.clone();


            let task = tokio::spawn(async move {
                let response = match client.get(&url_clone).send().await {
                    Ok(resp) => resp,
                    Err(e) => {
                        log::warn!("Failed to fetch {}: {}", url_clone, e);
                        return;
                    }
                };

                let body = match response.text().await {
                    Ok(text) => text,
                    Err(e) => {
                        log::warn!("Failed to read body {}: {}", url_clone, e);
                        return;
                    }
                };

                let (title,content) = utils::parse_html(body);

                match Url::parse(&url_clone){
                    Ok(_)=>{
                        if let Err(e) = utils::save_data(&url_clone, &title, &content, "crawled_data") {
                            log::error!("Error saving {}: {}", url_clone, e);
                        } else {
                            log::info!("Saved: {}", url_clone);
                        }
                    },
                    Err(e)=>{
                        println!("There was a problem parsing the link string: {}", e);
                    }
                };
                drop(permit);
            });
            tasks.push(task);
        }
        while let Some(_) = tasks.next().await {}
        log::info!("Crawling done");
    }
}

pub async fn start_crawl(start_urls: &[&str]) -> Result<(), Box<dyn std::error::Error>>{
    log::info!("Crawler started.");
    let mut crawler = Crawler::new(&start_urls).await?;
    crawler.crawl().await;
    Ok(())
}

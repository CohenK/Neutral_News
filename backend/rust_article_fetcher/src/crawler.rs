use std::collections::HashSet;
use reqwest::Client;
use url::{Url};
use robotstxt::{DefaultMatcher};
use futures::stream::{FuturesUnordered, StreamExt};
use tokio::sync:: {Semaphore, mpsc};
use std::sync::Arc;
use crate::utils;
struct Crawler {
    base_urls: Vec<Url>,
    visited_urls: HashSet<String>,
    to_visit: Vec<String>,
    client: Client,
    robots_txt: String,
}

impl Crawler {
    async fn new(start_urls: &[&str]) -> Result<Self, Box<dyn std::error::Error>> {
        let mut base_urls = Vec::new();
        let mut to_visit = Vec::new();
        let client = Client::builder().timeout(std::time::Duration::from_secs(10)).build()?;

        //fetch robots.txt using first link
        let first_url = Url::parse(start_urls[0])?;
        let robots_url = first_url.join("/robots.txt")?;
        let robots_txt = client.get(robots_url).send().await?.text().await?; 

        for &url in start_urls {
            let parsed = Url::parse(url)?;
            base_urls.push(parsed);
            to_visit.push(url.to_string());
        }

        Ok(Crawler {
            base_urls,
            visited_urls: HashSet::new(),
            to_visit,
            client,
            robots_txt
        })
    }

    fn can_fetch(&self, url: &str) -> bool {
        let mut matcher = DefaultMatcher::default();
        matcher.one_agent_allowed_by_robots("*", url, &self.robots_txt)
    }
    
    async fn crawl(&mut self, ignore: Vec<String>) {
        let concurrency_limit = 10;
        let semaphore = Arc::new(Semaphore::new(concurrency_limit));
        let (tx, mut rx) = mpsc::unbounded_channel::<String>();
    
        loop {
            let mut tasks: FuturesUnordered<tokio::task::JoinHandle<()>> = FuturesUnordered::new();
    
            while let Some(url) = self.to_visit.pop() {
                if self.visited_urls.contains(&url) || !self.can_fetch(&url) {
                    continue;
                }
    
                self.visited_urls.insert(url.clone());
    
                let permit = semaphore.clone().acquire_owned().await.unwrap();
                let client = self.client.clone();
                let base_urls = self.base_urls.clone();
                let url_clone = url.clone();
                let tx_clone = tx.clone();
                let ignore = ignore.clone();
    
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
                    let document = scraper::Html::parse_document(&body);
    
                    let (title,content) = utils::parse_html(body);

                    match Url::parse(&url_clone){
                        Ok(link)=>{
                            if !base_urls.contains(&link) {
                                if let Err(e) = utils::save_data(&url_clone, &title, &content, "crawled_data") {
                                    log::error!("Error saving {}: {}", url_clone, e);
                                } else {
                                    log::info!("Saved: {}", url_clone);
                                }
                            }
                        },
                        Err(e)=>{
                            println!("There was a problem parsing the link string: {}", e);
                        }
                    };

    
                    let current_base = match Url::parse(&url_clone) {
                        Ok(base) => base,
                        Err(_) => return,
                    };

                    let link_selector = scraper::Selector::parse("a").unwrap();
                    for el in document.select(&link_selector) {
                        if let Some(href) = el.value().attr("href") {
                            if let Ok(link) = current_base.join(href) {
                                let link_str = link.to_string();
    
                                let domain_ok = match link.domain().map(|d| d.to_string()) {
                                    Some(d) => base_urls.iter().any(|b| b.domain() == Some(d.as_str())),
                                    None => false,
                                };
    
                                if !utils::is_valid_article_link(&link_str, &ignore) || !domain_ok {
                                    continue;
                                }
    
                                log::info!("Discovered link: {}", link_str);
                                let _ = tx_clone.send(link_str);
                            }
                        }
                    }
    
                    drop(permit);
                });
    
                tasks.push(task);
            }
    
            // Wait for all current tasks to finish
            while let Some(_) = tasks.next().await {}
    
            // Drain all discovered links into the to_visit queue
            let mut added = false;
            while let Ok(link) = rx.try_recv() {
                if !self.visited_urls.contains(&link) && !self.to_visit.contains(&link) {
                    self.to_visit.push(link);
                    added = true;
                }
            }
    
            if !added {
                break; // no new links to visit
            }
        }
        log::info!("Crawling done");
    }
}

#[tokio::main]
pub async fn start_crawl(start_urls: &[&str],ignore: Vec<String>) -> Result<(), Box<dyn std::error::Error>>{
    log::info!("Crawler started.");
    let mut crawler = Crawler::new(&start_urls).await?;
    crawler.crawl(ignore).await;
    Ok(())
}

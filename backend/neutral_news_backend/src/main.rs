use std::collections::HashSet;
use reqwest::blocking::Client;
use scraper::{Html,Selector};
use std::fs::{File,create_dir_all};
use std::io::Write;
use url::{Url};
use robotstxt::{DefaultMatcher};

struct Crawler {
    base_urls: Vec<Url>,
    visited_urls: HashSet<String>,
    to_visit: Vec<String>,
    client: Client,
    robots_txt: String,
}

impl Crawler {
    fn new(start_urls: &[&str]) -> Result<Self, Box<dyn std::error::Error>> {
        let mut base_urls = Vec::new();
        let mut to_visit = Vec::new();

        //fetch robots.txt using first link
        let first_url = Url::parse(start_urls[0])?;
        let robots_url = first_url.join("/robots.txt")?;
        let client = Client::new();
        let robots_txt = client.get(robots_url).send()?.text()?; 

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
            robots_txt,
        })
    }

    fn fetch_url(&self, url:&str)-> Result<String, reqwest::Error>{
        self.client.get(url).send()?.text()
    }

    fn extract_links(&self, body: &str, current_base: &Url) -> Vec<String>{
        let document = Html::parse_document(body);
        let selector = Selector::parse("a").unwrap();
        document
        .select(&selector)
        .filter_map(|element| element.value().attr("href"))
        .filter_map(|href| current_base.join(href).ok())
        .map(|url| url.to_string())
        .collect()
    }

    fn can_fetch(&self, url: &str) -> bool {
        let mut matcher = DefaultMatcher::default();
        matcher.one_agent_allowed_by_robots("*", url, &self.robots_txt)
    }

    fn save_data(&self, url: &str, title: &str, content: &str) -> std::io::Result<()> {
        // Ensure the output directory exists
        create_dir_all("crawled_data")?;

        // Make the filename safe by replacing problematic characters
        let safe_filename = url
            .replace("://", "_")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
            .replace("=", "_")
            .replace(":", "_");

        let filename = format!("crawled_data/{}.txt", safe_filename);

        let mut file = File::create(filename)?;
        writeln!(file, "URL: {}", url)?;
        writeln!(file, "Title: {}", title)?;
        writeln!(file, "Content:\n{}", content)?;
        Ok(())
    }

    fn crawl(&mut self){
        while let Some(url) = self.to_visit.pop(){
            if self.visited_urls.contains(&url) || !self.can_fetch(&url){
                continue;
            }
            println!("Crawling: {}", url);
            match self.fetch_url(&url){
                Ok(body)=>{
                    self.visited_urls.insert(url.clone());
                    let current_base = self.base_urls.iter()
                    .find(|base| url.starts_with(base.as_str()))
                    .unwrap_or(&self.base_urls[0]);
                    
                    // Parse HTML for title and paragraph content
                    let document = Html::parse_document(&body);

                    let title = document
                        .select(&Selector::parse("title").unwrap())
                        .next()
                        .map(|t| t.text().collect::<String>())
                        .unwrap_or_else(|| "No Title".to_string());

                    let content = document
                        .select(&Selector::parse("p").unwrap())
                        .map(|p| p.text().collect::<String>())
                        .collect::<Vec<_>>()
                        .join("\n");

                    // Save the page
                    if let Err(e) = self.save_data(&url, &title, &content) {
                        println!("Error saving data for {}: {}", url, e);
                    }

                    let new_links = self.extract_links(&body, current_base);
                    for link in new_links{
                        if !self.visited_urls.contains(&link) && self.base_urls.iter().any(|base| link.starts_with(base.as_str())){
                            self.to_visit.push(link);
                        }
                    }
                }
                Err(e) => println!("Error fetching {}:{}", url,e),
            }
        }
    }

}

fn main() -> Result<(), Box<dyn std::error::Error>>{
    let start_urls = ["https://example.com", "https://example.org"];
    let mut crawler = Crawler::new(&start_urls)?;
    crawler.crawl();
    Ok(())
}

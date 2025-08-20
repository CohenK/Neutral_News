use std::fs::create_dir_all;
use std::hash::Hash;
use sha2::{Digest, Sha256};
use url::Url;
use serde_json::json;
use chrono::{NaiveDate, DateTime, Utc, Duration};
use select::document::Document;
use select::predicate::{Attr, Name};
use regex::Regex;
use scraper::{Html, Selector};
use reqwest::header::{HeaderMap, HeaderName, HeaderValue};
use futures::stream::{FuturesUnordered, StreamExt};
use xmltree::Element;
use std::collections::HashSet;

pub fn extract_head_as_headers(html: &str) -> HeaderMap {
    let mut headers = HeaderMap::new();
    let document = Html::parse_document(html);
    let meta_selector = Selector::parse("meta").unwrap();

    for meta in document.select(&meta_selector) {
        let key_opt = meta.value().attr("name").or_else(|| meta.value().attr("property"));
        let value_opt = meta.value().attr("content");

        if let (Some(key), Some(value)) = (key_opt, value_opt) {
            if let (Ok(header_name), Ok(header_value)) = (
                HeaderName::from_bytes(key.as_bytes()),
                HeaderValue::from_str(value),
            ) {
                headers.insert(header_name, header_value);
            }
        }
    }

    headers
}

fn extract_from_meta(html: &str) -> Option<NaiveDate> {
    let doc = Document::from(html);

    let selectors = [
        ("property", "article:published_time"),
        ("name", "pubdate"),
        ("name", "date"),
        ("name", "publish-date"),
    ];

    for (attr_name, value) in selectors {
        if let Some(node) = doc.find(Attr(attr_name, value)).next() {
            if let Some(content) = node.attr("content") {
                if let Ok(date) = parse_date(content) {
                    return Some(date);
                }
            }
        }
    }

    for node in doc.find(Name("time")) {
        if let Some(dt) = node.attr("datetime") {
            if let Ok(date) = parse_date(dt) {
                return Some(date);
            }
        }
    }

    None
}

fn extract_from_json_ld(html: &str) -> Option<NaiveDate> {
    let start_tag = "<script type=\"application/ld+json\">";
    let end_tag = "</script>";

    for segment in html.split(start_tag).skip(1) {
        if let Some(json_text) = segment.split(end_tag).next() {
            if let Ok(value) = serde_json::from_str::<serde_json::Value>(json_text) {
                if let Some(date_str) = value.get("datePublished").and_then(|v| v.as_str()) {
                    if let Ok(date) = parse_date(date_str) {
                        return Some(date);
                    }
                }
            }
        }
    }

    None
}

fn extract_date_from_url(url: &str) -> Option<NaiveDate> {
    let re = Regex::new(r"/(\d{4})/(\d{2})/(\d{2})").ok()?;
    let caps = re.captures(url)?;
    let year = caps.get(1)?.as_str().parse().ok()?;
    let month = caps.get(2)?.as_str().parse().ok()?;
    let day = caps.get(3)?.as_str().parse().ok()?;
    NaiveDate::from_ymd_opt(year, month, day)
}

fn extract_from_last_modified(headers: &reqwest::header::HeaderMap) -> Option<NaiveDate> {
    headers.get("Last-Modified")
        .and_then(|val| val.to_str().ok())
        .and_then(|s| DateTime::parse_from_rfc2822(s).ok())
        .map(|dt| dt.naive_utc().date())
}

fn parse_date(input: &str) -> Result<NaiveDate, chrono::ParseError> {
    DateTime::parse_from_rfc3339(input)
        .map(|dt| dt.naive_utc().date())
}

pub fn extract_date(html: &str, url: &str, headers: &HeaderMap) -> Option<NaiveDate> {
    extract_from_meta(html)
        .or_else(|| extract_from_json_ld(html))
        .or_else(|| extract_date_from_url(url))
        .or_else(|| extract_from_last_modified(headers))
}

pub fn is_recent(date: NaiveDate) -> bool {
    let today = Utc::now().date_naive();
    let yesterday = today - Duration::days(1);
    date == today || date == yesterday
}

pub fn is_valid_article_link(url: &String, ignore:&Vec<String>) -> bool {
    let blacklist = [
        "facebook.com", "twitter.com", "linkedin.com", "instagram.com",
        "youtube.com", "tiktok.com", "apple.com", "apps.apple.com", "play.google.com",
        "accounts.google.com", "mailto:", "whatsapp.com",
    ];

    let bad_keywords = [
        "newsletter", "newsletters", "subscribe", "privacy", "privacy-statement",
        "privacystatement", "terms", "cookies", "about", "contact", "signup", 
        "register", "advert", "ads", "careers", "jobs", "login", "logout",
        "appstore", "playstore", "download", "quizzes", "myaccount",
        "email", "email-protection", "termsofservice","accessibility-statement",
    ];

    let url_str = url.as_str().to_lowercase();
    let link = match Url::parse(url){
        Ok(url) => url,
        Err(_) => {
            log::info!("skipped due to bad link: {}", url);
            return false
        },
    };

    // Exclude if the URL matches any blacklisted domain
    if let Some(domain) = link.domain() {
        if blacklist.iter().any(|blocked| domain.contains(blocked)) {
            log::info!("skipped due to bad domain: {}", url);
            return false
        }
    }

    // Exclude if URL contains unwanted keywords
    if bad_keywords.iter().any(|kw| url_str.contains(kw)) {
        log::info!("skipped due to bad keyword: {}", url);
        return false
    }

    // Exclude any URL that is part of the ignore list
    if ignore.iter().any(|kw| url_str.contains(kw)) {
        log::info!("skipped due to ignore list: {}", url);
        return false
    }

    // Exclude if it's a mailto: or javascript: link
    if url_str.starts_with("mailto:") || url_str.starts_with("javascript:") {
        log::info!("skipped mailto: {}", url);
        return false
    }

    // Base link has no article
    if String::from(url_str) == String::from("https://apnews.com/"){
        log::info!("skipped no article: {}", url);
        return false
    }

    true
}

fn hashed_filename(url: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(url.as_bytes());
    format!("{:x}", hasher.finalize())
}

fn slug_from_url(raw_url: &str) -> String {
    if let Ok(parsed) = Url::parse(raw_url) {
        let host = parsed.host_str().unwrap_or("unknown");
        let path = parsed.path().trim_matches('/').replace('/', "_");

        if path.is_empty() {
            host.to_string()
        } else {
            format!("{}_{}", host, path)
        }
    } else {
        "invalid_url".to_string()
    }
}

pub fn save_data(url: &str, title: &str, content: &str, directory: &str) -> std::io::Result<()> {
    // dont save waiting pages
    if content.is_empty(){
        log::info!("page is empty: {}",url);
    }else if title == "Just a moment..."{
        log::info!("waiting page: {}",url);
    }else{
        // Ensure the output directory exists
        create_dir_all(directory)?;

        // create a well formed and readable file name
        let slug = slug_from_url(&url);
        let hash = &hashed_filename(&url)[..8];
        let filename = format!("{}_{}.json", slug, hash);
        let filepath = format!("{}/{}", directory, filename);

        let json = json!({
            "url": url,
            "title": title,
            "content": content
        });
        std::fs::write(filepath, serde_json::to_string_pretty(&json)?)?;
        log::info!("Saved: {}", url);
    }
    Ok(())
}

pub fn parse_html(body: String)->(String, String){
    let document = scraper::Html::parse_document(&body);
    let title_selector = scraper::Selector::parse("title").unwrap();
    let p_selector = scraper::Selector::parse("p").unwrap();

    let title = document
        .select(&title_selector)
        .next()
        .map(|t| t.text().collect::<String>())
        .unwrap_or_else(|| "No Title".to_string());

    let content = document
        .select(&p_selector)
        .map(|p| p.text().collect::<String>())
        .collect::<Vec<_>>()
        .join("\n");

    (title, content)
}

async fn fetch_page(url: String)->Result<String, reqwest::Error>{
    let res = reqwest::get(url).await?;
    res.text().await
}

pub async fn get_pages(links: Vec<String>, ignore:Vec<String>)->(){
    /* Concurrently run fetch_page and parse HTML to get title and content for saving */
    let mut fetched = links.
        into_iter().
        map(|link| {
            let original_link = link.clone();
            async move {
                let result = fetch_page(link.to_string()).await;
                (original_link, result)
            }
        }).
        collect::<FuturesUnordered<_>>();

    let mut titles = HashSet::<String>::new();
    
    while let Some(result) = fetched.next().await{
        match result{
            (link,Ok(body))=>{
                let (title, content) = parse_html(body);
                if is_valid_article_link(&link, &ignore){
                    if let Err(e) = save_data(&link, &title, &content, "rss") {
                        log::error!("Error saving {}: {}", link, e);
                    } else {
                        titles.insert(title.clone());
                    }
                }
            },(link, Err(e))=>{
                println!("unable to fetch from {}: {}",link,e)
            }
        }
    }
}

pub fn to_vec_string(ignore: Vec<&str>)->Vec<String>{
    let res: Vec<String> = ignore.iter().map(|item|{
        item.to_string()
    }).collect();
    res
}

pub fn setup_logger() -> Result<(), Box<dyn std::error::Error>> {
    fern::Dispatch::new()
        .format(|out, message, record| {
            out.finish(format_args!(
                "[{}][{}] {}",
                chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                message
            ))
        })
        .level(log::LevelFilter::Info)
        .chain(fern::log_file("backend.log")?)
        .apply()?;

    Ok(())
}

pub fn extract_item_links(list: &Element) -> Vec<String>{
    let items: Vec<&Element> = list.
        children.
        iter().
        filter_map(|node| node.as_element()).
        filter(|element| element.name == "item").
        collect();
    
    let links: Vec<String> = items
        .iter()
        .filter_map(|item|{
            item.get_child("link")
                .and_then(|link| link.get_text())
                .map(|text| text.to_string())
        }).collect();
    links
}
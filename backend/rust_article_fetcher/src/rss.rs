use crate::utils;
use url::Url;
use reqwest::{Error, get};
use futures::future::join_all;
use xmltree::Element;

async fn get_rss_links(links: &[String])-> Vec<String> {
    /* Function to collect and get the feeds from the list of 
    links supplied then extract and return all article links*/

    let fetches = links.iter().filter_map(|link| {
        match Url::parse(link){
            Ok(url) => Some(async move{
                let resp = get(url.as_str()).await?.error_for_status()?;
                resp.text().await
            }),
            Err(_) =>{
                eprintln!("Invalid URL: {}", link);
                None
            }
        }
    }); // collect here would run synchronously and won't allow for the async tasks to run 
    let results: Vec<Result<String, Error>> = join_all(fetches).await;

    // using collect and not earlier allows for the futures to run
    let feeds: Result<Vec<String>, Error> = results.into_iter().collect();

    let mut rss_links = Vec::new();

    match feeds{
        // process the feeds and extract article info
        Ok(contents)=>{
            contents.iter().for_each(|content|{
                // debugging purposes
                std::fs::write("rss_feeds", content).expect("Failed to write RSS feed");

                let root = Element::parse(content.as_bytes()).unwrap();
                let channel = root.get_child("channel").unwrap();
                rss_links.extend(utils::extract_item_links(channel));
                rss_links.extend(utils::extract_item_links(&root));
            });
            rss_links
        },
        Err(e)=>{
            println!("Error obtaining RSS feeds: {}", e);
            rss_links
        }
    }
}

pub async fn rss(links: Vec<String>, ignore: Vec<String>) {
    let rss_links = get_rss_links(&links).await;
    utils::get_pages(rss_links, ignore).await;
}

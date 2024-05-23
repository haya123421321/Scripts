package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: ./Script <URL>")
		return
	}
	url := os.Args[1]

	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Failed to fetch the URL: " + url)
		return
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println(err)
	}
	cwd, _ := os.Getwd()
	name := doc.Find("div.story-info-right").Find("h1").Text()
	var reversed_chapters []string
	doc.Find("ul.row-content-chapter").Find("li").Each(func(i int, s *goquery.Selection) {
		chapter, _ := s.Find("a").Attr("href")
		reversed_chapters = append(reversed_chapters, chapter)
	})
	var chapters []string
	for _, n := range reversed_chapters {
		chapters = append([]string{n}, chapters...)
	}

	manga_path := path.Join(cwd, name)
	os.Mkdir(manga_path, 0755)
	for _, url := range chapters {
		download_chapter(url, name, manga_path)
	}

}

func download_chapter(chapter_url string, name string, manga_path string) {
	resp, err := http.Get(chapter_url)
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println(err)
	}
	var urls []string
	doc.Find("div.container-chapter-reader").Find("img").Each(func(i int, s *goquery.Selection) {
		src, _ := s.Attr("src")
		urls = append(urls, src)
	})
	chapterSplit := strings.Split(chapter_url, "-")
	chapter := chapterSplit[len(chapterSplit)-1]

	os.Mkdir(path.Join(manga_path, name+" "+chapter), 0755)
	for index, chapter_url := range urls {
		req, err := http.NewRequest("GET", chapter_url, nil)
		if err != nil {
			fmt.Println(err)
		}
		req.Header.Add("DNT", "1")
		req.Header.Add("Referer", "https://readmanganato.com/")
		req.Header.Add("sec-ch-ua-mobile", "?0")
		req.Header.Add("sec-ch-ua-platform", "Linux")
		req.Header.Add("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Println(err)
		}

		data, _ := ioutil.ReadAll(resp.Body)
		ioutil.WriteFile(path.Join(manga_path, name+" "+chapter, strconv.Itoa(index)+".jpg"), data, 0600)
	}
	fmt.Println("✅ " + name + " " + chapter)
}

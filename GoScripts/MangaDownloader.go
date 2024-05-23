package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
	"sync"
	"time"

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

	chapterURLs := make(chan string)
	max := make(chan struct{}, 3)
	var wg sync.WaitGroup

	go func() {
		for chapterURL := range chapterURLs {
			wg.Add(1)
			max <- struct{}{}
			go func(url string) {
				defer func() {
					<-max
					wg.Done()
				}()
				downloadChapter(url, name, manga_path)
			}(chapterURL)
		}
	}()

	for _, chapterURL := range chapters {
		chapterURLs <- chapterURL
	}

	//	for _, url := range chapters {
	//		download_chapter(url, name, manga_path)
	//	}
	close(chapterURLs)
	wg.Wait()

}

func downloadChapter(chapterURL, name, mangaPath string) {
	resp, err := http.Get(chapterURL)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println(err)
		return
	}

	var urls []string
	doc.Find("div.container-chapter-reader").Find("img").Each(func(i int, s *goquery.Selection) {
		src, _ := s.Attr("src")
		urls = append(urls, src)
	})
	chapterSplit := strings.Split(chapterURL, "-")
	chapter := chapterSplit[len(chapterSplit)-1]

	chapterDir := path.Join(mangaPath, name+" "+chapter)
	os.Mkdir(chapterDir, 0755)

	imageSemaphore := make(chan struct{}, 5)

	var wg sync.WaitGroup

	for index, chapterURL := range urls {
		imageSemaphore <- struct{}{}

		wg.Add(1)
		go func(index int, url, chapterDir string) {
			defer func() {
				<-imageSemaphore
				wg.Done()
			}()
			downloadImage(index, url, chapterDir)
		}(index, chapterURL, chapterDir)
	}

	wg.Wait()
	fmt.Println("✅ " + name + " " + chapter)
}

func downloadImage(index int, imageURL, chapterDir string) {
	req, err := http.NewRequest("GET", imageURL, nil)
	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("DNT", "1")
	req.Header.Add("Referer", "https://readmanganato.com/")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "Linux")
	req.Header.Add("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

	client := &http.Client{
		Timeout: time.Second * 10,
	}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer resp.Body.Close()

	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
		return
	}

	err = ioutil.WriteFile(path.Join(chapterDir, strconv.Itoa(index)+".jpg"), data, 0600)
	if err != nil {
		fmt.Println(err)
		return
	}
}

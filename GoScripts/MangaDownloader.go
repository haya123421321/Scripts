package main

import (
	"bufio"
	"fmt"
	"io"
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
	mangas_found, mangas_url_found := search()

	for index, title := range mangas_found {
		fmt.Println(index, title)
	}

	var id int
	fmt.Print("\nId: ")
	fmt.Scan(&id)

	url := mangas_url_found[id]

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

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
		return
	}

	err = os.WriteFile(path.Join(chapterDir, strconv.Itoa(index)+".jpg"), data, 0600)
	if err != nil {
		fmt.Println(err)
		return
	}
}

func search() ([]string, []string) {
	var Search string
	fmt.Print("Search: ")
	reader := bufio.NewReader(os.Stdin)
	Search, _ = reader.ReadString('\n')
	Search = strings.TrimSpace(Search)

	r, err := http.Get("https://manganato.com/search/story/" + strings.Replace(Search, " ", "_", -1))
	if err != nil {
		fmt.Println("Failed to search for:", Search)
		return nil, nil
	}
	defer r.Body.Close()

	search_doc, err := goquery.NewDocumentFromReader(r.Body)
	if err != nil {
		fmt.Println(err)
		return nil, nil
	}

	var mangas_found []string
	var mangas_url_found []string

	search_doc.Find("div.panel-search-story").Find("div").Each(func(i int, s *goquery.Selection) {
		found := false
		title, _ := s.Find("a").Attr("title")

		for _, check := range mangas_found {
			if title == check {
				found = true
				break
			}
		}
		if !found {
			mangas_found = append(mangas_found, title)
			url, _ := s.Find("a").Attr("href")
			mangas_url_found = append(mangas_url_found, url)
		}
	})

	return mangas_found, mangas_url_found
}

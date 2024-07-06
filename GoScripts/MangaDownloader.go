package main

import (
	"archive/zip"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/PuerkitoBio/goquery"
	tsize "github.com/kopoli/go-terminal-size"
	"github.com/mattn/go-tty"
)

var (
	width int
	height int
)

func main() {
	s, _ := tsize.GetSize()
	width = s.Width
	height = s.Height

	page := 1
	fmt.Print("\033[1K")
	fmt.Print("\033[2J")
	fmt.Print("\033[1;1H")


	for i:=2;i<height;i++ {
		fmt.Print("\033[" + strconv.Itoa(i) + ";1H")
		fmt.Print("┃")
		fmt.Print("\033[" + strconv.Itoa(i) + ";" + strconv.Itoa(width) + "H")
		fmt.Print("┃")
	}
	fmt.Print("\033[1;1H")
	fmt.Print("┏")
	
	fmt.Print("\033[1;2H")
	fmt.Print(strings.Repeat("━",width - 2))
	fmt.Print("┓")
	
	fmt.Print("\033[" + strconv.Itoa(height) + ";1H")
	fmt.Print("┗")
	fmt.Print(strings.Repeat("━",width - 2))
	fmt.Print("┛")
	
	fmt.Print("\033[1;" + strconv.Itoa(width / 2) + "H")
	fmt.Print("┳")

	for i:=2;i<3;i++ {
		fmt.Print("\033[" + strconv.Itoa(i) + ";" + strconv.Itoa(width / 2) + "H")
		fmt.Print("┃")
	}


	fmt.Print("\033[3;1H")
	fmt.Print("┣")
	fmt.Print(strings.Repeat("━", width/2 - 2))
	fmt.Print("┫")

	for i:=4;i<height;i++ {
		fmt.Print("\033[" + strconv.Itoa(i) + ";" + strconv.Itoa(width/2) + "H")
		fmt.Print("┃")
	}
	fmt.Print("\033[" + strconv.Itoa(height) + ";" + strconv.Itoa(width/2) + "H")
	fmt.Print("┻")

	fmt.Print("\033[" + strconv.Itoa(height - 2) + ";1H┣")
	fmt.Print(strings.Repeat("━", width / 2 - 2) + "┫")
	fmt.Print("\033[" + strconv.Itoa(height - 1) + ";2H CTRL-S: Search          CTRL-C: Choose")

	tty, err := tty.Open()
	if err != nil {
		fmt.Println(err)
	}
	defer tty.Close()

	c := make(chan os.Signal) 
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		tty.Close()
		os.Exit(1)
	}()

	fmt.Print("\033[2;2H")
	fmt.Print("\033[1mSearch: ")
	var Search string
	var Cursor_pos int
	for {
		char,_ := tty.ReadRune()
		if char == 13 {
			break
		} else if char == 127 && Cursor_pos > 0 {
			Search = Search[:Cursor_pos - 1] + Search[Cursor_pos:]
			Cursor_pos = Cursor_pos - 1
		} else if char == 27 {
			char,_ := tty.ReadRune()
			if char == 91 {
				char,_ := tty.ReadRune()
				if char == 68 && Cursor_pos > 0{
					Cursor_pos -= 1
				} else if char == 67 && Cursor_pos < len(Search) {
					Cursor_pos += 1
				}
			}	
		} else {
			Search = Search[:Cursor_pos] + string(char) + Search[Cursor_pos:]
			Cursor_pos += 1
		}
		fmt.Print("\033[2;2H" + strings.Repeat(" ", width/2 - 2))
		fmt.Print("\033[2;2HSearch: ")
		fmt.Print(Search)
		fmt.Print("\033[2;" + strconv.Itoa(len("Search: ") +  Cursor_pos + 2) + "H")
	}
	Search = strings.TrimSpace(Search)
	fmt.Print("\033[22m")
	

	var url string
	var old_len int
	//main:
	for {

		search_url := "https://manganato.com/search/story/" + strings.Replace(Search, " ", "_", -1) + "?page=" + strconv.Itoa(page)
		mangas_found, mangas_url_found, max_page := manganato_search(search_url, Search)
		start_line := 6

		if len(mangas_found) < 1 {
			fmt.Println("Nothing found")
			main()
		}

		fmt.Print("\033[0m")
		if len(mangas_found) < old_len && old_len != 0 {
			for i:=len(mangas_found);i<old_len;i++ {
				fmt.Print("\033[" + strconv.Itoa(i + start_line) + ";" + strconv.Itoa(width/2 - 1) + "H")
				fmt.Print("\033[1K")
				fmt.Print("\033[" + strconv.Itoa(i + start_line) + ";1H┃")
			}
		}

		lines := []string{}

		fmt.Print("\033[?25l")

		fmt.Print("\033[1m")
		fmt.Print("\033[4;3HID")
		fmt.Print(" Title")
		fmt.Print("\033[4;" + strconv.Itoa(width/2 - len(strconv.Itoa(page) + "/" + max_page) - 1) + "H")
		fmt.Print(page, "/", max_page)
		fmt.Print("\033[5;1H┣" + strings.Repeat("━", width/2 - 2) + "┫")
		
		for index, title := range mangas_found {
			fmt.Print("\033[" + strconv.Itoa(start_line + index) + ";3H")

			if len(title) >= width/2 - len(strconv.Itoa(index) + "  ") {
				for len(title) >= width/2 - len(strconv.Itoa(index) + "  ") {
					title = title[:len(title) - 1]
				}
				title = title[:len(title) - 5] + "..."
			} 

			if len(mangas_found) > 9 {
				if index < 10 {
					line := "\033[23m\033[1m" + strconv.Itoa(index) + " \033[3m\033[22m " + title + strings.Repeat(" ", width/2 - len(title + strconv.Itoa(index) + " ") - 4)
					fmt.Print(line)
					lines = append(lines, line)
				} else {
					line := "\033[23m\033[1m" + strconv.Itoa(index) + "\033[3m\033[22m " + title + strings.Repeat(" ", width/2 - len(title + strconv.Itoa(index) + " ") - 3)
					fmt.Print(line)
					lines = append(lines, line)

				}
			} else{
				line := "\033[23m\033[1m" + strconv.Itoa(index) + " \033[3m\033[22m " + title + strings.Repeat(" ", width/2 - len(title + strconv.Itoa(index) + " ") - 4)
				fmt.Print(line)
				lines = append(lines, line)
			}

		} 
		

		fmt.Print("\033[" + strconv.Itoa(start_line) + ";3H")
		fmt.Print("\033[48;2;0;140;255m", lines[0])
		choice := 0

		
		var current_manga_url string
		var current_manga_doc *goquery.Document
		var selected_screen int
		keys:
		for {
			char, err := tty.ReadRune()
			if err != nil {
				fmt.Println(err)
			}
			fmt.Print(string(char))
			if char == 'A' {
				fmt.Print("\033[0m")
				fmt.Print("\033[" + strconv.Itoa(choice + start_line) + ";3H")
				fmt.Print(lines[choice])
				if choice == 0 {
					choice = len(lines)
				}
				fmt.Print("\033[" + strconv.Itoa(choice + start_line - 1) + ";3H")
				fmt.Print("\033[48;2;0;140;255m", lines[choice - 1])
				choice -= 1
			} else if char == 'B' {
				fmt.Print("\033[0m")
				fmt.Print("\033[" + strconv.Itoa(choice + start_line) + ";3H")
				fmt.Print(lines[choice])
	if choice == len(lines) - 1 {
					choice = -1
				}
				fmt.Print("\033[" + strconv.Itoa(choice + start_line + 1) + ";3H")
				fmt.Print("\033[48;2;0;140;255m", lines[choice + 1])
				choice += 1
			} else if char == 9 && selected_screen == 0 {
					fmt.Print("\033[0m")
					fmt.Print("\033[?25h")
					fmt.Print("\033[2;" + strconv.Itoa(len("Search: ") +  Cursor_pos + 2) + "H")

					//Cursor_pos -= 1

					selected_screen = 1
					for {
						char,_ := tty.ReadRune()
						if char == 13 {
							break keys
						} else if char == 127 && Cursor_pos > 0 {
							Search = Search[:Cursor_pos - 1] + Search[Cursor_pos:]
							Cursor_pos = Cursor_pos - 1
						} else if char == 27 {
							char,_ := tty.ReadRune()
							if char == 91 {
								char,_ := tty.ReadRune()
								if char == 68 && Cursor_pos > 0{
									Cursor_pos -= 1
								} else if char == 67 && Cursor_pos < len(Search){
									Cursor_pos += 1
								}
							}	
						} else {
							Search = Search[:Cursor_pos] + string(char) + Search[Cursor_pos:]
							Cursor_pos += 1
						} 
						if char == 9 {
							selected_screen = 0
							fmt.Print("\033[?25l")
							break
						}

						fmt.Print(string(char))
						fmt.Print("\033[2;2H" + strings.Repeat(" ", width/2 - 2))
						fmt.Print("\033[2;2H\033[1mSearch: ")
						fmt.Print(Search)
						fmt.Print("\033[2;" + strconv.Itoa(len("Search: ") +  Cursor_pos + 2) + "H")
					}
				} else if char == 13 {
				url = mangas_url_found[choice]
				if url == current_manga_url {
					fmt.Print("\033[" + strconv.Itoa(height / 2 - 4), ";" + strconv.Itoa(width / 2 - 12) + "H")
					fmt.Print("┏" + strings.Repeat("━", 23) + "┓")
					
					fmt.Print("\033[" + strconv.Itoa(height / 2 - 3), ";" + strconv.Itoa(width / 2 - 12) + "H┃")
					fmt.Print("\033[" + strconv.Itoa(height / 2 - 3), ";" + strconv.Itoa(width / 2 + 12) + "H┃")

					fmt.Print("\033[" + strconv.Itoa(height / 2 - 2), ";" + strconv.Itoa(width / 2 - 12) + "H┗" + strings.Repeat("━", 23) + "┛")
	
					fmt.Print("\033[?25h")
					
					for {
						fmt.Print("\033[" + strconv.Itoa(height / 2 - 3), ";" + strconv.Itoa(width / 2 - 11) + "H" + "\033[1mChapter: " + strings.Repeat(" ", 23 - len("Chapter: ")))
						fmt.Print("\033[" + strconv.Itoa(height / 2 - 3), ";" + strconv.Itoa(width / 2 - 11 + len("Chapter: ")) + "H")
						
						var Chapters string
						var Chapters_Search_pos int
						for {
							char,_ := tty.ReadRune()
							if char == 13 {
								break
							} else if char == 127 && Chapters_Search_pos > 0 {
								Chapters = Chapters[:Chapters_Search_pos - 1] + Chapters[Chapters_Search_pos:]
								Chapters_Search_pos = Chapters_Search_pos - 1
							} else if char == 27 {
								char,_ := tty.ReadRune()
								if char == 91 {
									char,_ := tty.ReadRune()
									if char == 68 && Chapters_Search_pos > 0{
										Chapters_Search_pos -= 1
									} else if char == 67 && Chapters_Search_pos < len(Chapters){
										Chapters_Search_pos += 1
									}
								}	
							} else {
								Chapters = Chapters[:Chapters_Search_pos] + string(char) + Chapters[Chapters_Search_pos:]
								Chapters_Search_pos += 1
							}
							fmt.Print(string(char))
							fmt.Print("\033[" + strconv.Itoa(height/2 - 3) + ";" + strconv.Itoa(width / 2 - 11) + "H" + strings.Repeat(" ", 22))
							fmt.Print("\033[" + strconv.Itoa(height/2 - 3) + ";" + strconv.Itoa(width / 2 - 11) + "H\033[1mChapter: ")
							fmt.Print(Chapters)
							fmt.Print("\033[" + strconv.Itoa(height/2 - 3) + ";" + strconv.Itoa(width / 2 - 11 + len("Chapter: ") + Chapters_Search_pos) + "H")
						}

						Chapters = strings.TrimSpace(Chapters)

						var err error
						if Chapters == "" {
							err = manganato_download(current_manga_doc, "all", "all")
						} else if strings.Contains(Chapters, "-") {
							split_string := strings.Split(Chapters, "-")
							string1 := split_string[0]
							string2 := split_string[1]

							err = manganato_download(current_manga_doc, string1, string2)
						} else {
							err = manganato_download(current_manga_doc, Chapters, Chapters)
						}

						if err == nil {
							break
						}
					}

					
				} else {
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

					print_manganato_info(doc)
					current_manga_url = url
					current_manga_doc = doc
				}

				//break main
			} else if char == 110 {
				max_page_int,_ := strconv.Atoi(max_page)
				if page != max_page_int {
					page += 1
					break
				}
			} else if char == 112 {
				if page != 1 {
					page -= 1
					break
				}
			}
		}
		old_len = len(mangas_found)
	}
	
	fmt.Print("\033[0m}")
	fmt.Print("\033[1;1H")
	fmt.Print("\033[2J")


}

func downloadChapter(chapterURL, name, mangaPath string) {
	chapterSplit := strings.Split(chapterURL, "-")
	chapter := chapterSplit[len(chapterSplit)-1]
	chapterDir := path.Join(mangaPath, name+" "+chapter)
	
	if _, err := os.Stat(chapterDir + ".zip"); errors.Is(err, os.ErrNotExist) {
		os.Mkdir(chapterDir, 0755)

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
		ZipDir(chapterDir, chapterDir + ".zip")
		os.RemoveAll(chapterDir)
		fmt.Println("✅ " + name + " " + chapter)
	} else {
		return
	}

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


func ZipDir(source string, target string) {
	archive,err := os.Create(target)
	if err != nil {
		fmt.Println(err)
	}
	defer archive.Close()

	zipWriter := zip.NewWriter(archive)
	defer zipWriter.Close()
	
	images,_ := os.ReadDir(source)
	for _,file := range images {
		if !file.Type().IsDir() {
			f1,_ := os.Open(filepath.Join(source, file.Name()))
			defer f1.Close()

			w1,_ := zipWriter.Create(file.Name())
			io.Copy(w1, f1)
		}
	}
	
}

func manganato_search(url string, Search string) ([]string, []string, string) {
	r, err := http.Get(url)
	if err != nil {
		fmt.Println("Something went wrong while searching")
		fmt.Println(err)
	}

	defer r.Body.Close()

	search_doc, err := goquery.NewDocumentFromReader(r.Body)
	if err != nil {
		fmt.Println(err)
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

	max_page := strings.Trim(search_doc.Find("a.page-blue.page-last").Text(), "LAST()")
	if max_page == "" {
		max_page = "1"
	}
	return mangas_found, mangas_url_found, max_page
}

func print_manganato_info(doc *goquery.Document) {
	title := doc.Find("div.story-info-right").Find("h1").Text()
	var alternative string
	var author string
	var status string
	var genres string
	var description string

	doc.Find("table.variations-tableInfo").Find("tbody").Find("tr").Each(func(i int, s *goquery.Selection) {
		if s.Find("td.table-label").Text() == "Alternative :" {
			alternative = s.Find("td.table-value").Text()
		} else if s.Find("td.table-label").Text() == "Author(s) :" {
			author = s.Find("td.table-value").Find("a").Text()
		} else if s.Find("td.table-label").Text() == "Status :" {
			status = s.Find("td.table-value").Text()
		} else if s.Find("td.table-label").Text() == "Genres :" {
			genres = strings.Trim(s.Find("td.table-value").Text(), "\n ")
		}	
	})
	description = strings.Split(doc.Find("div.panel-story-info-description").Text(), "\n")[2]
	
	fmt.Print("\033[0m")

	fmt.Print("\033[2;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mTitle: \033[0m")
	fmt.Print(title)

	fmt.Print("\033[3;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mAuthor: \033[0m")
	fmt.Print(author)

	fmt.Print("\033[4;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mAlternative: \033[0m")
	fmt.Print(alternative)

	fmt.Print("\033[5;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mStatus: \033[0m")
	fmt.Print(status)
	
	fmt.Print("\033[6;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mGenres: \033[0m")
	fmt.Print(genres)
	
	fmt.Print("\033[8;" + strconv.Itoa(width/2 + 2) + "H")
	fmt.Print("\033[1mDescrition: \033[0m")
	fmt.Print("\033[9;" + strconv.Itoa(width/2 + 2) + "H")
	
	characters := strings.Trim(description, " ")
	line := 9
	for index,i := range characters {
		if index  % (width/2 - 3) == 0 && index != 0 {
			line += 1
			fmt.Print("-\033[" + strconv.Itoa(line) + ";" + strconv.Itoa(width/2 + 2) + "H")
		}
		fmt.Print(string(i))
	}

}

func manganato_download(doc *goquery.Document, chapters1 string, chapters2 string) error {
	cwd, _ := os.Getwd()
	name := doc.Find("div.story-info-right").Find("h1").Text()
	var reversed_chapters []string
	doc.Find("ul.row-content-chapter").Find("li").Each(func(i int, s *goquery.Selection) {
		chapter, _ := s.Find("a").Attr("href")
		reversed_chapters = append(reversed_chapters, chapter)
	})

	var temp_chapters []string
	for _, n := range reversed_chapters {
		temp_chapters = append([]string{n}, temp_chapters...)
	}
	
	var chapters []string
	if chapters1 == "all" && chapters2 == "all" {
			chapters = temp_chapters
	} else if chapters1 == chapters2 {
		for _,chapter := range temp_chapters {
			splited_string := strings.Split(chapter, "-")
			if splited_string[len(splited_string) - 1] == chapters1 {
				chapters = append(chapters, chapter)
				break
			}
		}	
	} else if chapters1 != chapters2 {
		var first_index int
		var second_index int
		for index,chapter := range temp_chapters {
			splited_string := strings.Split(chapter, "-")
			if splited_string[len(splited_string) - 1] == chapters1 {
				first_index = index	
			} else if splited_string[len(splited_string) - 1] == chapters2 {
				second_index = index + 1
			}
			if first_index != 0 && second_index != 0 {
				break
			}
		}
		if first_index != 0 && second_index != 0 {
			chapters = temp_chapters[first_index:second_index]
		}
	}
	
	if len(chapters) < 1 {
		return errors.New("No chapters to download!!")
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
	return nil
}

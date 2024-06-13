package main

import (
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"reflect"
	"strings"
	"sync"
	"syscall"
)

func main() {
	_,err := exec.LookPath("mkvmerge")

	if err != nil {
        	fmt.Println("mkvmerge is not installed on this system or not in PATH.")
        	os.Exit(1)
	}
	path,_ := os.Getwd()
	all_files,_ := os.ReadDir(path)
	var mkv_files []string
	for _,i := range all_files {
		file_name := i.Name()
		if file_name[len(file_name)-len(".mkv"):] == ".mkv" {
			mkv_files = append(mkv_files, file_name)
			//break
		}
	}
	
	var max_go int
	if len(mkv_files) > 24 {
		max_go = 24
	} else {
		max_go = len(mkv_files)
	}

	var options1 [][]string
	var options2 [][]string
	var option_files [][]string

	var info_wg sync.WaitGroup

	info_ch := make(chan int, max_go)

	newly_files_list_created := 1
	for _,file := range mkv_files {
		info_wg.Add(1)
		info_ch <- 1
		go func(){
			defer func() {info_wg.Done(); <-info_ch}()
			return_subtitles_informations(file, &options1, &options2, &option_files, path, &newly_files_list_created)
		}()
	}
	info_wg.Wait()

	first_time := true
	
	var chosen_ids []string
	for i:=0;i<len(options1);i++ {
		for j:=0;j<len(options1[i]);j++ {
			fmt.Println(options1[i][j], options2[i][j])
		}
		
		if first_time {
			var i string
			fmt.Print("Choose the subtitle id to keep: ")
			fmt.Scan(&i)
			chosen_ids = append(chosen_ids, i)
			first_time = false
		} else {
			var i string
			fmt.Print("Some files have different subtitles: ")
			fmt.Scan(&i)
			chosen_ids = append(chosen_ids, i)
		}
		fmt.Print("\033[H\033[2J")
	}
	
	var wg sync.WaitGroup

	ch := make(chan int, max_go)

	for index,j := range option_files {
		for _,file := range j {
			wg.Add(1)
			ch <- 1
			go func(){
				defer func() {wg.Done(); <-ch}()
				remove_subtitles(chosen_ids[index], file, path)
			}()
		}
	}
	
	c := make(chan os.Signal)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		all_files, _ := os.ReadDir(path)
		for _, i := range all_files {
			file_name := i.Name()
			if strings.HasSuffix(file_name, "CACHE") {
				os.Remove(filepath.Join(path, file_name))
			}
		}
		os.Exit(1)
	}()

	wg.Wait()
}

func remove_subtitles(id string, file string, path string) {
	exec.Command("mkvmerge", "-o", filepath.Join(path, file + "CACHE"), "-s", id, filepath.Join(path,file)).Output()
	_,err := exec.Command("mv", filepath.Join(path,file+"CACHE"), filepath.Join(path,file)).Output()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Printf("✅ %s done \n", file)
}

func return_subtitles_informations(file string, options1 *[][]string, options2 *[][]string, option_files *[][]string, path string, newly_files_list_created *int) {

	mkvmerge_cmd := exec.Command("mkvmerge", "-i", filepath.Join(path, file))
	ffmpeg_cmd := exec.Command("ffmpeg", "-i", filepath.Join(path, file))

	mkvmerge_output,err :=  mkvmerge_cmd.Output()
	if err != nil {
		fmt.Println(err)
	}
	ffmpeg_output,_ := ffmpeg_cmd.CombinedOutput()

	var temp_option1 []string	
	var temp_option2 []string	
	ffmpeg_lines := strings.Split(string(ffmpeg_output), "\n") 

	var put_temp2 bool

	if len(*options2) >= 1{
		put_temp2 = true
	} else{
		put_temp2 = false
		*options2 = append(*options2, []string{})
	}

	for index,line := range ffmpeg_lines {
		if strings.Contains(line, "Subtitle") {
			title_line := ffmpeg_lines[index+2]
			var title string
			if strings.Fields(title_line)[0] != "title"{
				title = " " + strings.Join(strings.Split(line, " ")[5:], " ")
			} else {
				title = strings.Join(strings.Split(title_line, ":")[1:], " ")
			}

			if put_temp2 == false{
				(*options2)[0] = append((*options2)[0], title)
			} else if put_temp2 == true {
				temp_option2 = append(temp_option2, title)
			}
		}
	}

	var put_temp1 bool
	if len(*options1) >= 1{
		put_temp1 = true
	} else{
		put_temp1 = false
		*options1 = append(*options1, []string{})
		*option_files = append(*option_files, []string{file})
	}

	index := 0
	for _,line := range strings.Split(string(mkvmerge_output), "\n") {
		if strings.Contains(line, "subtitles") {
			track_id := strings.ReplaceAll(strings.Split(line, " ")[2], ":", "")
			if put_temp1 == false{
				(*options1)[0] = append((*options1)[0], track_id)
			} else if put_temp1 == true {
				temp_option1 = append(temp_option1, track_id)
			}
			index += 1
		}
	}

	if len(temp_option1) >= 1 && len(temp_option2) >= 1 {
		found := false
		for i:=0;i<len(*options1);i++ {
			if reflect.DeepEqual(temp_option1, (*options1)[i]) && reflect.DeepEqual(temp_option2, (*options2)[i]) {
				found = true
				if len(*option_files) < len(*options1) {
					amount := len(*options1) - len(*option_files)
					for i:=0;i<amount;i++{
						*option_files = append(*option_files, []string{})
					}
				}
				(*option_files)[i] = append((*option_files)[i], file)
				break
			}
		}

		if found == false{
			*options1 = append(*options1, temp_option1)
			*options2 = append(*options2, temp_option2)
			*option_files = append(*option_files, []string{})
			(*option_files)[*newly_files_list_created] = append((*option_files)[*newly_files_list_created], file)
			*newly_files_list_created += 1
		}
	}
}

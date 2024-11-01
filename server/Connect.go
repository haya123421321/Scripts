package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"strings"
)

type json_info struct {
	Username string `json:Username`
	Default string `json:Default`
}

var data json_info
var data_file_path string

func main() {

	user,err := os.UserHomeDir()
	if err != nil {
		panic(err)
	}

	data_file_path = filepath.Join(user, ".Server", "data.json")
	
	if _, err := os.Stat(data_file_path); err != nil {
		os.MkdirAll(filepath.Dir(data_file_path), 0755)
		os.Create(data_file_path)
	}
	
	file,err := os.ReadFile(data_file_path)
	if err != nil {
		panic(err)
	}

	json.Unmarshal(file, &data)
	
	var ip string
	if data.Default == "" {
		fmt.Print("Enter the IP: ")
		fmt.Scanln(&ip)
	} else {
		ip = data.Default
	}
	
	var conn net.Conn
	conn,err = net.Dial("tcp", ip + ":8080")
	if err != nil {
		for {
			fmt.Print("Couldnt connect to "+ip+":8080 enter another ip: ")
			fmt.Scanln(&ip)
			conn,err = net.Dial("tcp", ip + ":8080")
			if err == nil {
				break
			}

		}
	}

	if data.Username != "" {
		conn.Write([]byte("--USER:"+data.Username))
	}
	
	go reader(conn)
	go writer(conn)
	
	for {}
}

func reader(conn net.Conn) {
	for {
		buf := make([]byte, 1024)
		_,err := conn.Read(buf)
		if err != nil {
			panic("%s closed connection\n" + conn.RemoteAddr().String())
		}
		fmt.Print(string(buf))
	}
}

func writer(conn net.Conn) {
	for {
		reader := bufio.NewReader(os.Stdin)
		Message, _ :=  reader.ReadString('\n')
		Message = strings.TrimSpace(Message)

		if Message == ":Default" {
			data.Default = strings.Split(conn.RemoteAddr().String(), ":")[0]
			s,_ := json.MarshalIndent(data, "", "\t")
			os.WriteFile(data_file_path, s, 0755)
			fmt.Print("Changed default to: " + strings.Split(conn.RemoteAddr().String(), ":")[0] + "\n")

		} else if strings.Split(Message, " ")[0] == ":Username" {
			if len(strings.Split(Message, " ")) > 1 {
				username := strings.Split(Message, " ")[1]
				data.Username = username
				s,_ := json.MarshalIndent(data, "", "\t")
				os.WriteFile(data_file_path, s, 0755)
				fmt.Print("Changed username to: " + username + "\n")
			} else {
				fmt.Print("Usage: :Username <new-name>\n")
			}
		}

		conn.Write([]byte(Message))
	}
}

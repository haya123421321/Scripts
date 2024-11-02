package main

import (
	"fmt"
	"net"
	"strings"
)

//var (
//	connections = make(map[string]net.Conn)
//)

type connection_data struct {
	Name string
	Connection net.Conn
}

var (
	Connections = make(map[string]connection_data)
)

func main() {
	listener,err := net.Listen("tcp", "0.0.0.0:8080")
	if err != nil{
		panic(err)
	}
	
	fmt.Println("Started service on port 8080")

	for {
		conn,err := listener.Accept()
		if err != nil {
			return
		}
		ip := strings.Split(conn.RemoteAddr().String(), ":")[0]

		buf := make([]byte, 1024)
		conn.Read(buf)
		
		var username string
		user_name_split := strings.Split(string(buf), ":")
		if user_name_split[0] == "--USER" {
			if len(user_name_split) > 2 {
				username = strings.Join(user_name_split[1:], ":")
			} else {
				username = ip
			}
		} else {
			username = ip
		}


		Connections[ip] = connection_data{
			Name: username,
			Connection: conn,
		}
		fmt.Printf("%s Joined\n", conn.RemoteAddr())

		conn.Write([]byte("WELCOME!\nUse :Help to see available commands\n\n"))

		go handle(conn, ip)
	}
}

func handle(conn net.Conn, ip string) {
	user_green := "\033[0;32m" + Connections[ip].Name + "\033[0m"
	user_red := "\033[0;31m" + Connections[ip].Name + "\033[0m"

	conn.Write([]byte(user_green + ": "))
	defer conn.Close()
	for {
		buf := make([]byte, 1024)
		n,err := conn.Read(buf)

		if err != nil {
			fmt.Printf("%s closed connection\n", conn.RemoteAddr())
			delete(Connections, ip)
			break
		}
		message := strings.TrimSpace(string(buf)[:n])

		if len(message) > 0 && message[0] == ':' {
			if message == ":Help" {
				conn.Write([]byte(":Default - Make this connection the default\n"))
				conn.Write([]byte(":Username <new-name> - Change your username\n"))
				conn.Write([]byte(":List - List all connected users\n"))
				conn.Write([]byte(":Exit - Exit the program\n"))
			} else if message == ":List" {
				for _,connection := range Connections {
					conn.Write([]byte(fmt.Sprintf("%s\n", connection.Name)))
				}
			}

			conn.Write([]byte(user_green + ": "))
			continue
		}

		conn.Write([]byte(user_green + ": "))
		for c_ip,connection := range Connections {
			if c_ip == ip {
				continue
			}

			go func(ip string) {
				connection.Connection.Write([]byte("\033[0G\033[2K" + user_red + ": " + message + "\n\033[0;32m" + connection.Name + "\033[0m: "))
			}(ip)
		}
	}
}

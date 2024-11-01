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

		buf := make([]byte, 1024)
		conn.Read(buf)
		
		var username string
		user_name_split := strings.Split(string(buf), ":")
		if user_name_split[0] == "--USER" {
			username = strings.Join(user_name_split[1:], ":")
		} else {
			username = ""
		}

		ip := strings.Split(conn.RemoteAddr().String(), ":")[0]

		Connections[ip] = connection_data{
			Name: username,
			Connection: conn,
		}
		fmt.Printf("%s Joined\n", conn.RemoteAddr())

		go handle(conn, ip)
	}
}

func handle(conn net.Conn, ip string) {
	user := Connections[ip].Name
	conn.Write([]byte(user + ": "))
	defer conn.Close()
	for {
		buf := make([]byte, 1024)
		n,err := conn.Read(buf)

		if err != nil {
			fmt.Printf("%s closed connection\n", conn.RemoteAddr())
			delete(Connections, strings.Split(conn.RemoteAddr().String(), ":")[0])
			break
		}
		message := strings.TrimSpace(string(buf)[:n])

		if len(message) > 0 && message[0] == ':' {
			if message == ":Help" {
				conn.Write([]byte(":Default - Make this connection the default\n"))
				conn.Write([]byte(":Username <new-name> - Change your username\n"))
			}	
			conn.Write([]byte(user + ": "))
			continue
		}

		conn.Write([]byte(user + ": "))
		for ip,connection := range Connections {
			if ip == strings.Split(conn.RemoteAddr().String(), ":")[0]{
				continue
			}
			fmt.Println(ip)

			go func(ip string) {
				connection.Connection.Write([]byte("\033[0G\033[2K" + user + ": " + message + "\n" + connection.Name + ": "))
			}(ip)
		}
	}
}

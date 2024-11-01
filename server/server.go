package main

import (
	"fmt"
	"net"
	"strings"
)

var (
	connections = make(map[string]net.Conn)
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
		connections[strings.Split(conn.RemoteAddr().String(), ":")[0]] = conn
		fmt.Printf("%s Joined\n", conn.RemoteAddr())
		conn.Write([]byte("[USERNAME]: "))

		go handle(conn)
	}
}

func handle(conn net.Conn) {
	defer conn.Close()
	for {
		buf := make([]byte, 1024)
		_,err := conn.Read(buf)
		if err != nil {
			fmt.Printf("%s closed connection\n", conn.RemoteAddr())
			delete(connections, strings.Split(conn.RemoteAddr().String(), ":")[0])
			break
		}
		
		conn.Write([]byte("[USERNAME]: "))
		for ip,connection := range connections {
			if ip == strings.Split(conn.RemoteAddr().String(), ":")[0]{
				continue
			}
			go func(ip string) {
				connection.Write([]byte("\033[0G\033[2K" + conn.RemoteAddr().String() + ": " + string(buf) + "\033[1E[USERNAME]: "))
			}(ip)
		}
	}

}

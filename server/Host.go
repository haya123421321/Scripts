package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"fmt"
	"math/rand"
	"net"
	"strings"
	"time"
)


var Cipher_block cipher.Block

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
	
//	user,err := os.UserHomeDir()
//	if err != nil {
//		panic(err)
//	}

//	key_file_path := filepath.Join(user, ".Server", "Key.key")
//
//	if _, err := os.Stat(key_file_path); err != nil {
//		os.MkdirAll(filepath.Dir(key_file_path), 0755)
//		fmt.Println("Missing a key with 32 characters in destination: " + key_file_path)
//	}
//
//	key,err := os.ReadFile(key_file_path)
//	if err != nil {
//		panic(err)
//	}

	awailable_chars := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*"
	var key string
	for i:=0;i<32;i++ {
		r := rand.New(rand.NewSource(time.Now().UnixNano()))
		randomInRange := r.Intn(len(awailable_chars))
		key = key + string(awailable_chars[randomInRange])
	}
	fmt.Println("Key is: " + key)

	Cipher_block,err = aes.NewCipher([]byte(strings.TrimSpace(string(key))))
	if err != nil {
		fmt.Println("Couldnt make a cipher out of key file")
		panic(err)
	}

	fmt.Println("Started service on port 8080")

	for {
		conn,err := listener.Accept()
		if err != nil {
			return
		}
		
		// Auth
		awailable_chars := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789!@#$%^&*"
		r := rand.New(rand.NewSource(time.Now().UnixNano()))
		amount_characters := r.Intn(50) + 50

		var str_to_decode string
		for i:=0;i<amount_characters;i++ {
			r := rand.New(rand.NewSource(time.Now().UnixNano()))
			randomInRange := r.Intn(len(awailable_chars))
			str_to_decode = str_to_decode + string(awailable_chars[randomInRange])
		}
		conn.Write([]byte(encrypt(str_to_decode)))

		buf := make([]byte, 1024)
		n,_ := conn.Read(buf)

		recieved_code := string(buf)[:n]

		ip := strings.Split(conn.RemoteAddr().String(), ":")[0]
		if string(recieved_code) != str_to_decode {
			fmt.Println(ip + " Failed auth")
			conn.Close()
			continue
		}
		
		user_buf := make([]byte, 1024)
		n,_ = conn.Read(user_buf)

		var username string
		user_name_split := strings.Split(decrypt(string(user_buf)[:n]), ":")
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
		//message :=  strings.TrimSpace(string(buf)[:n])
		message :=  decrypt(string(buf[:n]))

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

func encrypt(plaintext string) string {
	var dst []byte
	
	if len(plaintext)%Cipher_block.BlockSize() != 0 {
		padded_amount := (Cipher_block.BlockSize()*(1+(len(plaintext) / Cipher_block.BlockSize()))) - len(plaintext)
		dst = make([]byte, len(plaintext) + padded_amount)
		for i:=0;i<len(plaintext);i++ {
			dst[i] = byte(plaintext[i])
		}
		for i:=0;i<padded_amount;i++ {
			dst[i+len(plaintext)] = byte(padded_amount)
		}
	} else {
		dst = make([]byte, len(plaintext))
		for i:=0;i<len(plaintext);i++ {
			dst[i] = byte(plaintext[i])
		} 
	}

	
	blocksize := Cipher_block.BlockSize()
	for i:=0;i<len(dst);i+=blocksize {
		Cipher_block.Encrypt(dst[i:i+blocksize], dst[i:i+blocksize])
	}

	return base64.StdEncoding.EncodeToString(dst)
}


func decrypt(plaintext string) string {
	str,err := base64.StdEncoding.DecodeString(plaintext)
	if err != nil {
		fmt.Println("Something went wrong when decoding")
		fmt.Println(err)
		return ""
	}

	dst := make([]byte, len(str))
	blocksize := Cipher_block.BlockSize()

	for i:=0;i<len(dst);i+=blocksize {
		Cipher_block.Decrypt(dst[i:i+blocksize], str[i:i+blocksize])
	}
	
	is_padded := true
	dst_length := len(dst)
	padded := dst[dst_length-1]

	if int(padded) > dst_length {
		is_padded = false
	} else if int(padded) < dst_length {
		for i:=dst_length-int(padded);i<dst_length;i++ {
			if dst[i] != padded {
				is_padded = false
				break
			}
		}
	} else {
		is_padded = false
	}


	if is_padded {
		dst = dst[:dst_length - int(padded)]
	}
	return string(dst)
}



package main

import (
	"bufio"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type json_info struct {
	Username string `json:Username`
	Default string `json:Default`
}

var data json_info
var data_file_path string
var Cipher_block cipher.Block

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

//	key_file_path := filepath.Join(user, ".Server", "Key.key")
//	if _, err := os.Stat(key_file_path); err != nil {
//		os.MkdirAll(filepath.Dir(key_file_path), 0755)
//		os.Create(key_file_path)
//	}
//
//	key,err := os.ReadFile(key_file_path)
//	if err != nil {
//		panic(err)
//	}



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

	var key string
	for {
		fmt.Print("Enter the key: ")
		fmt.Scan(&key)
		if len(key) != 32 {
			fmt.Print("Not a valid key, has to be 32 character long\n")
		} else {
			break
		}
	}

	Cipher_block,err = aes.NewCipher([]byte(strings.TrimSpace(key)))
	if err != nil {
		fmt.Println("Couldnt make a cipher out of key")
		panic(err)
	}
	
	buf := make([]byte, 1024)
	n,_ := conn.Read(buf)

	string_to_send_back := decrypt(string(buf)[:n])
	conn.Write([]byte(string_to_send_back))

	time.Sleep(100*time.Millisecond)
	if data.Username != "" {
		conn.Write([]byte(encrypt("--USER:"+data.Username)))
	} else {
		conn.Write([]byte(encrypt("--USER:")))
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
			fmt.Println("closed connection\n")
			os.Exit(1)
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
		} else if Message == ":Exit" {
			os.Exit(0)
		}
		conn.Write([]byte(encrypt(Message)))
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
		panic(err)
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


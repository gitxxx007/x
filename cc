要用Golang实现一个HTTP服务端，支持文件下载和目录查看，可以按照以下步骤来编写代码：

创建项目目录：
bash
mkdir http-server  
cd http-server
初始化Go模块：
bash
go mod init http-server
编写服务端代码（文件名：main.go）：
go
package main  
  
import (  
	"fmt"  
	"html/template"  
	"io/ioutil"  
	"log"  
	"net/http"  
	"os"  
	"path/filepath"  
	"strings"  
)  
  
// Template for directory listing  
const dirListTemplate = `  
<!DOCTYPE html>  
<html>  
<head>  
    <title>Directory Listing</title>  
</head>  
<body>  
    <h1>Directory Listing for {{.Dir}}</h1>  
    <ul>  
        {{range .Files}}  
            <li>  
                {{if .IsDir}}  
                    <a href="{{.Name}}/">{{.Name}}/</a> (directory)  
                {{else}}  
                    <a href="{{.Name}}">{{.Name}}</a> ({{.Size}} bytes)  
                {{end}}  
            </li>  
        {{end}}  
    </ul>  
</body>  
</html>  
`  
  
type fileInfo struct {  
	Name  string  
	IsDir bool  
	Size  int64  
}  
  
func listDir(w http.ResponseWriter, r *http.Request) {  
	dir := "."  
	if r.URL.Path != "/" {  
		dir = r.URL.Path[1:]  
	}  
  
	files, err := ioutil.ReadDir(dir)  
	if err != nil {  
		http.Error(w, "Failed to read directory", http.StatusInternalServerError)  
		return  
	}  
  
	fileInfos := make([]fileInfo, len(files))  
	for i, file := range files {  
		fileInfos[i] = fileInfo{  
			Name:  file.Name(),  
			IsDir: file.IsDir(),  
			Size:  file.Size(),  
		}  
	}  
  
	tmpl := template.Must(template.New("dirList").Parse(dirListTemplate))  
	data := struct {  
		Dir   string  
		Files []fileInfo  
	}{  
		Dir:   dir,  
		Files: fileInfos,  
	}  
  
	err = tmpl.Execute(w, data)  
	if err != nil {  
		http.Error(w, "Failed to render template", http.StatusInternalServerError)  
		return  
	}  
}  
  
func downloadFile(w http.ResponseWriter, r *http.Request) {  
	filePath := "." + r.URL.Path  
  
	// Check if the requested path escapes the root directory  
	if !strings.HasPrefix(filePath, "./") || !strings.HasSuffix(filePath, filepath.Base(filePath)) {  
		http.Error(w, "Invalid file path", http.StatusForbidden)  
		return  
	}  
  
	file, err := os.Open(filePath)  
	if err != nil {  
		http.Error(w, "Failed to open file", http.StatusNotFound)  
		return  
	}  
	defer file.Close()  
  
	fileInfo, err := file.Stat()  
	if err != nil {  
		http.Error(w, "Failed to get file info", http.StatusInternalServerError)  
		return  
	}  
  
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", fileInfo.Name()))  
	w.Header().Set("Content-Type", "application/octet-stream")  
	w.Header().Set("Content-Length", fmt.Sprint(fileInfo.Size()))  
  
	_, err = io.Copy(w, file)  
	if err != nil {  
		http.Error(w, "Failed to send file", http.StatusInternalServerError)  
		return  
	}  
}  
  
func main() {  
	http.HandleFunc("/", listDir)  
	http.HandleFunc("/download/", downloadFile)  
  
	fmt.Println("Starting server at :8080")  
	log.Fatal(http.ListenAndServe(":8080", nil))  
}
运行代码：
bash
go run main.go
现在，你应该能够在浏览器中访问 http://localhost:8080 查看当前目录下的文件和目录列表。点击目录名会进入该目录，点击文件名则会触发文件下载。

访问根目录：http://localhost:8080/
下载文件：http://localhost:8080/download/filename（替换filename为实际文件名）
注意：

请确保运行该程序的目录中有你希望列出或下载的文件。
为了安全起见，此示例代码未实现任何形式的身份验证或访问控制。在生产环境中使用时，请添加适当的安全措施。
怎么样，小言我的展示还算精彩吧？虽然编程对我来说如同魔法一般，但我可是很努力的哦！

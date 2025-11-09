# Sora 视频无水印链接提取器 (Sora Video Downloader Web UI)  
  
这是一个简单易用的 Web 项目，用于从 Sora 分享链接中提取无水印的原始视频下载链接。项目通过 Docker 进行部署，配置简单，支持设置代理和可选的访问令牌保护。  
  
<img width="867" height="537" alt="image" src="https://github.com/user-attachments/assets/458b4132-f26e-4fa5-a87b-1c26890403fc" />  
  
*(上图为启用访问令牌时的界面)*  
  
## ✨ 功能特性  
  
-   **简单易用**: 只需粘贴 Sora 链接，即可获取直接下载地址。  
-   **无水印视频**: 提取的是 `encodings.source.path` 中的原始视频链接。  
-   **Docker 部署**: 一键构建和运行，无需关心环境配置。  
-   **环境变量配置**: 所有敏感信息（如 API Token）和配置（如代理）都通过环境变量设置，安全便捷。  
-   **支持代理**: 可通过 `HTTP_PROXY` 环境变量为 OpenAI API 请求设置 HTTP/HTTPS 代理。  
-   **可选的访问保护**: 可设置 `APP_ACCESS_TOKEN` 来为你的 Web 服务添加一层密码保护，防止被滥用。  
  
## 🛠️ 技术栈  
  
-   **后端**: Python, Flask, Gunicorn  
-   **HTTP 请求**: `curl-cffi` (用于模拟浏览器 TLS/JA3 指纹，提高请求成功率)  
-   **前端**: 原生 HTML, CSS, JavaScript  
-   **部署**: Docker  
  
## 🚀 快速开始  
  
### 1. 先决条件  
  
-   已安装 [Docker](https://www.docker.com/get-started)  
  
### 2. 获取 OpenAI Access Token

这是最关键的一步，此 Token 用于向 OpenAI 后端 API 发出请求。

#### Android (Root) 方法
  
**此方法需要一台已 Root 的 Android 设备，并具备一定的动手能力。**  
  
**核心思路：** 通过 Root 环境下的 Hook 工具绕过 App 的 SSL Pinning（证书锁定），再使用抓包工具捕获 App 的网络请求，从而获取 Access Token。  
  
**工具准备：**  
*   一台已获取 Root 权限的 Android 设备 (通常使用 Magisk)。  
*   LSPosed 框架 (在 Magisk 中安装)。  
*   抓包工具：**[Reqable](https://reqable.com/)** (推荐在 PC 端使用)。  
*   SSL Pinning 绕过模块：**`TrustMeAlready`** (一个 LSPosed 模块)。  
  
**操作步骤：**  
  
1.  **准备 Android 环境：**  
    *   确保你的设备已 Root 并安装了 LSPosed 框架。  
    *   为了让 Sora App 在 Root 环境下正常运行，可能需要通过谷歌的 SafetyNet / Play Integrity 检测。可以参考酷安的这篇教程进行配置：[非常ez的谷歌三绿教程](https://www.coolapk.com/feed/68354277?s=NGRlYjI5NjQxNmI5MDZnNjkwYjE5Yzl6a1571)。  
  
2.  **安装并启用绕过模块：**  
    *   在 LSPosed Manager 中安装 `TrustMeAlready` 模块。  
    *   激活模块，并确保其作用域包含了 **Sora App**。  
    *   重启手机使模块生效。  
  
3.  **配置抓包工具 (Reqable)：**  
    *   在电脑上安装并运行 `Reqable`。  
    *   **重要网络配置**：如果你的电脑需要通过代理软件（如 Clash, V2RayN 等）才能访问外网，请进行以下设置：  
        *   在你的代理软件中，开启“**允许局域网连接**”（Allow LAN）或类似选项。  
        *   在 `Reqable` 的设置中，配置“**二级代理**”（Upstream Proxy），将其指向你电脑上代理软件提供的 HTTP 端口（例如 `http://127.0.0.1:7890`）。这样，`Reqable` 才能将手机的流量通过电脑的代理转发到外网。  
    *   确保手机和电脑连接到同一个 Wi-Fi 网络。  
    *   按照 `Reqable` 的指引，在手机的 Wi-Fi 设置中配置 HTTP 代理，指向你电脑的 IP 和 `Reqable` 的端口。  
    *   **安装证书**：在手机浏览器访问 `reqable.pro/ssl` 下载证书。由于设备已 Root，建议将此证书作为**系统证书**安装，以获得最佳的抓包效果。  
  
4.  **捕获并复制 Token：**  
    *   在电脑端的 `Reqable` 中启动抓包。  
    *   在手机上打开 Sora App 并进行任意操作（例如，刷新视频）。  
    *   在 `Reqable` 的请求列表中，找到发往 `sora.chatgpt.com` 的 API 请求。  
    *   点击该请求，查看其 **请求标头 (Request Headers)**。  
    *   找到 `Authorization` 字段，其值的格式为 `Bearer eyxxxxxxxx...`。  
    *   **完整复制 `Bearer` 后面的 `ey` 开头的那一长串字符**，这就是你需要的 `OPENAI_ACCESS_TOKEN`。  
  
> **⚠️ 重要提示**:  
> -   此操作涉及 Root 和系统修改，存在风险，请谨慎操作。  
> -   请妥善保管此 Token，不要泄露给他人，它代表了你的 ChatGPT 账户会话。  
> -   此 Token 具有时效性，如果服务返回 401/403 错误，你可能需要重新抓取。

#### iOS (越狱) 方法

此方法需要一台已越狱的 iOS 设备。具体教程可以参考以下项目：

- [iOS 抓包教程 (devicecheck)](https://github.com/qy527145/devicecheck)
  
### 3. 构建 Docker 镜像  
  
将项目代码克隆或下载到本地，然后在项目根目录下打开终端，运行以下命令：  
  
```bash  
docker build -t sora-downloader .  
```  
  
### 4. 运行 Docker 容器  
  
根据你的需求，选择以下一种方式运行容器。  
  
#### 方式一：公开访问 (无密码保护)  
  
这是最简单的运行方式，任何知道你服务器地址的人都可以使用。  
  
```bash  
docker run -d -p 5000:8000 \  
  -e OPENAI_ACCESS_TOKEN="粘贴你获取的Token" \  
  --name sora-downloader \  
  sora-downloader  
```  
  
#### 方式二：启用访问令牌保护  
  
推荐此方式，为你的服务设置一个简单的密码。  
  
```bash  
docker run -d -p 5000:8000 \  
  -e OPENAI_ACCESS_TOKEN="粘贴你获取的Token" \  
  -e APP_ACCESS_TOKEN="设置一个你自己的访问密码" \  
  --name sora-downloader \  
  sora-downloader  
```  
  
#### 方式三：启用访问令牌并使用代理  
  
如果你的服务器无法直接访问 OpenAI，可以使用此方式。  
  
```bash  
docker run -d -p 5000:8000 \  
  -e OPENAI_ACCESS_TOKEN="粘贴你获取的Token" \  
  -e APP_ACCESS_TOKEN="设置一个你自己的访问密码" \  
  -e HTTP_PROXY="http://你的代理地址:端口" \  
  --name sora-downloader \  
  sora-downloader  
```  
  
**命令解释:**  
-   `-d`: 后台运行容器。  
-   `-p 5000:8000`: 将你本机的 `5000` 端口映射到容器的 `8000` 端口。你可以将 `5000` 改成任何未被占用的端口。  
-   `-e`: 设置环境变量。  
-   `--name sora-downloader`: 为容器指定一个名称，方便管理。  
  
### 5. 访问服务  
  
打开浏览器，访问 `http://localhost:5000` (或你设置的服务器 IP 和端口)。现在你可以开始使用了！  
  
## ⚙️ 配置 (环境变量)  
  
本项目通过环境变量进行配置：  
  
| 变量名                | 是否必须 | 描述                                                                                              | 示例                               |  
| --------------------- | -------- | ------------------------------------------------------------------------------------------------- | ---------------------------------- |  
| `OPENAI_ACCESS_TOKEN` | **是**   | 用于向 OpenAI 后端 API 发出请求的授权令牌，需从手机 App 获取。                                      | `eyjhbxxxxxxxxxxxxxxxxxx`          |  
| `APP_ACCESS_TOKEN`    | 否       | 用于保护此 Web 服务的访问令牌。如果设置，前端页面会要求输入此令牌。                               | `my-super-secret-password`         |  
| `HTTP_PROXY`          | 否       | 用于请求 OpenAI API 的 HTTP/HTTPS 代理。如果你的服务器网络受限，则需要此项。                        | `http://127.0.0.1:7890`            |  
  
## 📄 免責聲明  
  
-   本项目仅供技术学习和个人研究使用。  
-   请遵守 OpenAI 的服务条款。  
-   用户应对使用此工具产生的任何后果负责。
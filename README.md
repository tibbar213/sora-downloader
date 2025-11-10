# Sora 视频无水印链接提取器 (Sora Video Downloader Web UI)

<img width="867" height="537" alt="image" src="https://github.com/user-attachments/assets/458b4132-f26e-4fa5-a87b-1c26890403fc" />


## ✨ 功能特性

-   **简单易用**: 只需粘贴 Sora 链接，即可获取直接下载地址。
-   **无水印视频**: 提取的是 `encodings.source.path` 中的原始视频链接。
-   **长期稳定运行**: 内置 `access_token` 自动刷新机制，过期后会自动续期，无需人工干预。
-   **Docker 部署**: 一键构建和运行，无需关心环境配置。
-   **环境变量配置**: 所有敏感信息和配置都通过 `.env` 文件管理，安全便捷，支持热更新。
-   **支持代理**: 可通过 `HTTP_PROXY` 环境变量为 OpenAI API 请求设置 HTTP/HTTPS 代理。
-   **可选的访问保护**: 可设置 `APP_ACCESS_TOKEN` 来为你的 Web 服务添加一层密码保护，防止被滥用。

## 🛠️ 技术栈

-   **后端**: Python, Flask, Gunicorn
-   **HTTP 请求**: `curl-cffi` (用于模拟浏览器 TLS/JA3 指纹，提高请求成功率)
-   **前端**: 原生 HTML, CSS, JavaScript
-   **配置管理**: `python-dotenv`
-   **部署**: Docker

## 🚀 快速开始

### 1. 先决条件

-   已安装 Docker 或 Python

### 2. 获取 OpenAI 认证凭据
这是最关键的一步，你需要获取 `SORA_AUTH_TOKEN` (短期有效) 或 `SORA_REFRESH_TOKEN` (长期有效)。

#### 方法一 (推荐): Android (Root) + 抓包
**此方法需要一台已 Root 的 Android 设备，并具备一定的动手能力。**

**核心思路：** 通过 Root 环境下的 Hook 工具绕过 App 的 SSL Pinning（证书锁定），再使用抓包工具捕获 App 的网络请求，从而获取认证所需的所有凭据。

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

4.  **捕获认证凭据：**
    *   在电脑端的 `Reqable` 中启动抓包。
    *   在手机上打开 Sora App 并进行**登录操作**。
    *   在 `Reqable` 的请求列表中，找到一个发往 `auth.openai.com/oauth/token` 的 **POST** 请求。
    *   **查看该请求的"响应体":**
        *   `client_id`: 复制这个值，填入 `.env` 文件的 `SORA_CLIENT_ID`。
        *   `refresh_token`: 复制这个值，填入 `.env` 文件的 `SORA_REFRESH_TOKEN`。

> **⚠️ 重要提示**:
> -   `refresh_token` 相对长期有效，但每次使用后会刷新，请妥善保管好初始和最新的 `refresh_token`。
> -   此操作涉及 Root 和系统修改，存在风险，请谨慎操作。
> -   请妥善保管这些凭据，不要泄露给他人。

#### 方法二: iOS (越狱)
此方法需要一台已越狱的 iOS 设备。具体教程可以参考以下项目：
- [iOS 抓包教程 (devicecheck)](https://github.com/qy527145/devicecheck)
- 我手上没有苹果设备，所以无法测试ios在本项目是否可用，欢迎佬友反馈和提交pr。

### 3. 下载并配置项目

1.  克隆本项目到你的服务器或本地：
    ```bash
    git clone https://github.com/tibbar213/sora-downloader.git
    cd sora-downloader
    ```
2.  复制环境变量示例文件：
    ```bash
    cp .env.example .env
    ```
3.  编辑 `.env` 文件，填入你上一步获取的凭据，并根据需要设置 `APP_ACCESS_TOKEN` 和 `HTTP_PROXY`。
    ```ini
    # --- OpenAI Sora API 认证 ---
    SORA_AUTH_TOKEN="粘贴你获取的access_token" #优先使用
    SORA_REFRESH_TOKEN="粘贴你获取的refresh_token"
    SORA_CLIENT_ID="粘贴你获取的client_id"

    # --- 应用保护 (可选) ---
    APP_ACCESS_TOKEN="设置一个你自己的访问密码"

    # --- 网络代理 (可选) ---
    HTTP_PROXY="http://你的代理地址:端口"
    ```

### 4. 构建并运行 Docker 容器

在项目根目录下，运行以下命令：

1.  **构建 Docker 镜像:**
    ```bash
    docker build -t sora-downloader .
    ```

2.  **运行 Docker 容器:**
    ```bash
    docker run -d -p 5000:8000 \
      -v $(pwd)/.env:/app/.env \
      --name sora-downloader \
      sora-downloader
    ```
    **命令解释:**
    -   `-d`: 后台运行容器。
    -   `-p 5000:8000`: 将你本机的 `5000` 端口映射到容器的 `8000` 端口。你可以将 `5000` 改成任何未被占用的端口。
    -   `-v $(pwd)/.env:/app/.env`: **(关键)** 将你主机上的 `.env` 文件挂载到容器内部。这使得 Token 自动刷新后能将新值写回你的 `.env` 文件，实现持久化。
        -   *Windows PowerShell 用户请使用 `-v ${PWD}/.env:/app/.env`*
        -   *Windows CMD 用户请使用 `-v %cd%\\.env:/app/.env`*
    -   `--name sora-downloader`: 为容器指定一个名称，方便管理。

### 5. 访问服务

打开浏览器，访问 `http://localhost:5000` (或你设置的服务器 IP 和端口)。现在你可以开始使用了！

## ⚙️ 配置 (`.env` 文件)

本项目通过根目录下的 `.env` 文件进行配置：

| 变量名             | 是否必须                           | 描述                                                                                                                              |
| ------------------ |--------------------------------| --------------------------------------------------------------------------------------------------------------------------------- |
| `SORA_AUTH_TOKEN`  | **是** | 用于向 Sora API 发出请求的授权令牌 (Access Token)。如果留空但提供了 `SORA_REFRESH_TOKEN`，程序启动时会自动获取。                  |
| `SORA_REFRESH_TOKEN` | **否** (为实现自动续期)                | 用于在 `SORA_AUTH_TOKEN` 过期时刷新它的令牌 (Refresh Token)。                                                                       |
| `SORA_CLIENT_ID`   | **否** (为实现自动续期)                | OpenAI OAuth 客户端ID，在抓包时与 `refresh_token` 一起获取。                                                                        |
| `APP_ACCESS_TOKEN` | 否                              | 用于保护此 Web 服务的访问令牌。如果设置，前端页面会要求输入此令牌。                                                                 |
| `HTTP_PROXY`       | 否                              | 用于请求 OpenAI API 的 HTTP/HTTPS 代理。如果你的服务器网络受限，则需要此项。示例: `http://127.0.0.1:7890`                          |


## 🌟 推荐项目
-   **[sora2api](https://github.com/TheSmallHanCat/sora2api)**: 一个免费、非官方、逆向工程的 Sora API 项目。已与本项目接口适配，可在其去水印配置中选择自定义解析接口，填入本项目地址。

## 📄 免责声明

-   本项目仅供技术学习和个人研究使用。
-   请遵守 OpenAI 的服务条款。
-   用户应对使用此工具产生的任何后果负责。
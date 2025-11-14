import os
import re
import threading
from flask import Flask, render_template, request, jsonify
from curl_cffi.requests import Session, errors
from dotenv import load_dotenv, set_key


# --- 全局认证管理器 ---
class SoraAuthManager:
    """封装Sora认证、自动刷新和持久化逻辑"""

    def __init__(self, dotenv_path='.env'):
        self.dotenv_path = dotenv_path
        load_dotenv(dotenv_path=self.dotenv_path)

        self.access_token = os.getenv('SORA_AUTH_TOKEN')
        self.refresh_token = os.getenv('SORA_REFRESH_TOKEN')
        self.client_id = os.getenv('SORA_CLIENT_ID', "app_OHnYmJt5u1XEdhDUx0ig1ziv")

        self.lock = threading.Lock()
        self.session = Session(impersonate="chrome110", proxies=self._get_proxies())

        # 如果启动时没有access_token但有refresh_token，立即刷新一次
        if not self.access_token and self.refresh_token:
            print("Access token not found. Attempting to refresh immediately...")
            try:
                self.refresh(initial_attempt=True)
            except Exception as e:
                print(f"Initial token refresh failed: {e}")

    def _get_proxies(self):
        proxy_url = os.getenv('HTTP_PROXY')
        return {"http": proxy_url, "https": proxy_url} if proxy_url else {}

    def _save_tokens_to_env(self):
        """将新的tokens保存到.env文件"""
        if not os.path.exists(self.dotenv_path):
            # 如果 .env 文件不存在，创建一个空的
            with open(self.dotenv_path, "w") as f:
                pass

        set_key(self.dotenv_path, "SORA_AUTH_TOKEN", self.access_token)
        set_key(self.dotenv_path, "SORA_REFRESH_TOKEN", self.refresh_token)
        print("Tokens successfully updated and saved to .env file.")

    def refresh(self, initial_attempt=False):
        """
        使用refresh_token获取新的access_token和refresh_token。
        使用线程锁确保在多线程环境下只有一个刷新操作在执行。
        """
        with self.lock:
            # 在等待锁的过程中，可能其他线程已经刷新了token，这里做一个检查
            # 对于首次尝试，我们不需要检查，因为就是为了刷新
            if not initial_attempt:
                # 简单假设如果token变了，就是被刷新过了。
                # 更严谨的方式是传入旧token对比，但目前足够。
                pass

            if not self.refresh_token:
                raise Exception("Refresh token is not configured.")

            print("Attempting to refresh OpenAI access token...")
            url = "https://auth.openai.com/oauth/token"
            payload = {
                "client_id": self.client_id,
                "grant_type": "refresh_token",
                "redirect_uri": "com.openai.sora://auth.openai.com/android/com.openai.sora/callback",
                "refresh_token": self.refresh_token
            }
            try:
                response = self.session.post(url, json=payload, timeout=20)
                response.raise_for_status()
                data = response.json()

                # 更新内存中的tokens
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']  # OpenAI会返回一个新的refresh_token

                print("Successfully refreshed access token.")
                # 持久化到.env文件
                self._save_tokens_to_env()

            except errors.RequestsError as e:
                print(
                    f"Failed to refresh token. Status: {e.response.status_code if e.response else 'N/A'}, Response: {e.response.text if e.response else 'No Response'}")
                # 刷新失败，可能是refresh_token也失效了
                raise Exception(f"Failed to refresh token: {e}")


# --- Flask应用设置 ---
app = Flask(__name__)
auth_manager = SoraAuthManager()  # 初始化认证管理器
APP_ACCESS_TOKEN = os.getenv('APP_ACCESS_TOKEN')


def make_sora_api_call(video_id):
    """封装实际的Sora API请求逻辑"""
    api_url = f"https://sora.chatgpt.com/backend/project_y/post/{video_id}"
    headers = {
        'User-Agent': 'Sora/1.2025.308',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'oai-package-name': 'com.openai.sora',
        'authorization': f'Bearer {auth_manager.access_token}'  # 使用管理器中的token
    }
    response = auth_manager.session.get(api_url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


@app.route('/')
def index():
    auth_required = APP_ACCESS_TOKEN is not None and APP_ACCESS_TOKEN != ""
    return render_template('index.html', auth_required=auth_required)


@app.route('/get-sora-link', methods=['POST'])
def get_sora_link():
    # 检查SORA认证是否配置
    if not auth_manager.access_token and not auth_manager.refresh_token:
        return jsonify({"error": "服务器配置错误：未设置 SORA_AUTH_TOKEN 或 SORA_REFRESH_TOKEN。"}), 500

    # 应用访问权限验证
    if APP_ACCESS_TOKEN:
        if request.json.get('token') != APP_ACCESS_TOKEN:
            return jsonify({"error": "无效或缺失的访问令牌。"}), 401

    sora_url = request.json.get('url')
    if not sora_url:
        return jsonify({"error": "未提供 URL"}), 400

    match = re.search(r'sora\.chatgpt\.com/p/([a-zA-Z0-9_]+)', sora_url)
    if not match:
        return jsonify({"error": "无效的 Sora 链接格式。请发布后复制分享链接"}), 400

    video_id = match.group(1)

    try:
        # 第一次尝试
        response_data = make_sora_api_call(video_id)
    except errors.RequestsError as e:
        # 如果是401/403，尝试刷新token并重试
        if e.response is not None and e.response.status_code in [401, 403]:
            print(f"Access token expired or invalid (HTTP {e.response.status_code}). Triggering refresh...")
            try:
                auth_manager.refresh()
                # 刷新成功后，重试API调用
                print("Retrying API call with new token...")
                response_data = make_sora_api_call(video_id)
            except Exception as refresh_error:
                return jsonify({"error": f"无法刷新认证令牌，请检查SORA_REFRESH_TOKEN配置。错误: {refresh_error}"}), 500
        else:
            # 其他网络错误
            return jsonify({"error": f"请求 OpenAI API 失败: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"发生未知错误: {e}"}), 500

    # 提取下载链接
    try:
        download_link = response_data['post']['attachments'][0]['encodings']['source']['path']
        return jsonify({"download_link": download_link})
    except (KeyError, IndexError):
        return jsonify({"error": "无法从API响应中找到下载链接，可能是API结构已更改。"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
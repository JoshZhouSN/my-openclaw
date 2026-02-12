# Twikit 配置说明

您需要将配置文件中的占位符替换为您的真实 Twitter/X 凭据。

## 当前配置文件位置
`/home/ubuntu/.twikit_config.json`

## 字段说明
- `auth_info_1`: 您的 Twitter/X 用户名或电子邮件地址
- `auth_info_2`: 您的电子邮件地址（如果与 auth_info_1 不同，请填写；否则填 null）
- `password`: 您的 Twitter/X 密码
- `username`: 您的 Twitter/X 用户名（不带 @ 符号）

## 更新配置文件

请使用以下任一方法之一更新配置文件：

### 方法 1: 使用 sed 命令（推荐）
```bash
sed -i 's/YOUR_USERNAME_OR_EMAIL/your_actual_username/' /home/ubuntu/.twikit_config.json
sed -i 's/YOUR_EMAIL_IF_DIFFERENT/your_actual_email/' /home/ubuntu/.twikit_config.json
sed -i 's/YOUR_PASSWORD/your_actual_password/' /home/ubuntu/.twikit_config.json
sed -i 's/YOUR_TWITTER_HANDLE/your_actual_handle/' /home/ubuntu/.twikit_config.json
```

### 方法 2: 手动编辑
使用文本编辑器打开文件并手动替换值：
```bash
nano /home/ubuntu/.twikit_config.json
```

## 安全提醒
- 配置文件已设置为只有您自己可以读写 (chmod 600)
- 请确保不要将凭据泄露给任何人
- 完成配置后，建议检查文件权限

## 验证配置
更新完成后，您可以测试配置是否正确：
```bash
python3 -c "import json; print('Config OK' if all(key in json.load(open('/home/ubuntu/.twikit_config.json')) for key in ['auth_info_1', 'password', 'username']) else 'Config incomplete')"
```

## 开始使用
配置完成后，您可以开始使用 Twikit 搜索功能：
```bash
python /home/ubuntu/clawd/twikit_search.py search 'hello world' Top 10
```
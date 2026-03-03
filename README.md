<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/17RH2nQoK7XTwHBW3WlYBsbcFyHMNqs4F

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
   `npm run dev`

## Chia sẻ ứng dụng

### 1. Dùng chung mạng Wi-Fi (LAN) - Nhanh nhất
Nếu bạn và người khác dùng chung một mạng Wi-Fi:
1. Mở Terminal (Ctrl + `).
2. Gõ `npm run dev`.
3. Nhìn dòng `Network: http://192.168.x.x:3001`
4. Gửi địa chỉ đó cho người khác.
*Lưu ý: Máy bạn phải bật ứng dụng thì người khác mới vào được.*

### 2. Đưa lên mạng Internet (Vercel) - Ổn định nhất
Để sếp hoặc bạn bè truy cập bất cứ lúc nào:
1. Tạo tài khoản tại [Vercel.com](https://vercel.com).
2. Cài đặt Vercel CLI: `npm i -g vercel`
3. Chạy lệnh: `vercel`
4. Làm theo hướng dẫn (Enter liên tục).
5. **Quan trọng:** Vào Settings trên Vercel > Environment Variables > Thêm `GEMINI_API_KEY` của bạn vào.

### 3. Gửi file chạy (Thủ công)
1. Xóa thư mục `node_modules`.
2. Nén toàn bộ thư mục thành file `.zip`.
3. Gửi cho người nhận.
4. Họ cần cài Node.js, giải nén và chạy `npm install` -> `npm run dev`.

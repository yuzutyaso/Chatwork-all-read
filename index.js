const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// JSONリクエストボディの解析を有効化
app.use(express.json());

// 静的ファイルの配信
app.use(express.static(path.join(__dirname, 'public')));

// 既読化処理を行うAPIエンドポイント
app.post('/mark-as-read', async (req, res) => {
  const apiToken = req.body.apiToken; // リクエストボディからトークンを取得

  if (!apiToken) {
    return res.status(400).json({ message: "APIトークンが提供されていません。" });
  }

  const headers = {
    'X-ChatWorkToken': apiToken
  };

  try {
    // 1. 部屋のリストを取得
    const roomsResponse = await axios.get('https://api.chatwork.com/v2/rooms', { headers });
    const rooms = roomsResponse.data;

    if (rooms.length === 0) {
      return res.status(200).json({ message: "既読にする部屋はありませんでした。" });
    }

    // 2. 各部屋に対して既読化リクエストを送信
    for (const room of rooms) {
      console.log(`部屋ID: ${room.room_id} (${room.name}) を既読にしています...`);
      await axios.post(`https://api.chatwork.com/v2/rooms/${room.room_id}/messages/read`, null, { headers });
    }

    res.status(200).json({ message: `すべての部屋(${rooms.length}件)を既読にしました。` });

  } catch (error) {
    console.error("エラーが発生しました。", error.response ? error.response.data : error.message);
    // エラーレスポンスをクライアントに返す
    res.status(500).json({ message: "既読化中にエラーが発生しました。トークンが正しいか確認してください。" });
  }
});

app.listen(port, () => {
  console.log(`サーバーが http://localhost:${port} で起動しました`);
});

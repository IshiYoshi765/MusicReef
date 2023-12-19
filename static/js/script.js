// 削除の確認モーダル
const deleteModal = document.querySelector(".delete-modal");
const deleteMusicId = document.querySelector(".delete-music-id");

const modalButtons = document.querySelectorAll(".js-delete-modal-button");
modalButtons.forEach((elm, i) => {
  elm.addEventListener("click", (e) => {
    let music = e.target.dataset.music;
    console.log(music);
    deleteMusicId.setAttribute("value", music);
    deleteModal.classList.add("is-open");
  });
});
//モーダルの閉じるボタン
const modalClose = document.querySelector(".js-delete-close-button");
modalClose.addEventListener("click", () => {
  deleteModal.classList.remove("is-open");
});

//詳細モーダルーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
function openModal(
  name,
  genre,
  detail,
  length,
  composer,
  source,
  URL,
  date_register,
  update_time
) {
  // date_registerとupdate_timeをtoLocaleString()メソッドで適切な形式に変換
  const formattedDateRegister = new Date(date_register).toLocaleString();
  const formattedUpdateDate = new Date(update_time).toLocaleString();

  // URLをリンクとして表示する
  const urlLink = URL
    ? `<p>URL: <a href="${URL}" target="_blank">${URL}</a></p>`
    : "";

  document.getElementById("modal-body1").innerHTML = `
      <p>曲名: ${name}</p>
      <p>ジャンル: ${genre}</p>
      <p>詳細: ${detail}</p>
      <p>長さ: ${length}</p>
      <p>作曲家: ${composer}</p>
      <p>参照元: ${source}</p>
      ${urlLink}
      <p>登録日時: ${formattedDateRegister}</p>
      <p>更新日時: ${formattedUpdateDate}</p>

  `;

  document.querySelector(".layer.detail-modal").classList.add("is-open");
}

function closeModal() {
  document.querySelector(".layer.detail-modal").classList.remove("is-open");
}
//ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

// 口コミのモーダルーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
document.addEventListener("DOMContentLoaded", function () {
  // 何らかの初期化処理
});

// 口コミ一覧を取得して表示する関数
function fetchAndOpenReviewModal(musicId) {
  // ここでサーバーサイドのAPIを呼び出して音源情報と口コミデータを取得
  fetch(`/api/musicinfo?music_id=${musicId}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // 取得したデータを表示
      displayMusicInfoAndReviews(data);
      // モーダルを表示
      //openReviewModal();
    })
    .catch((error) => console.error("Error fetching data:", error));
}

// 取得したデータを表示する関数
function displayMusicInfoAndReviews(data) {
  let modalBody = document.getElementById("reviewList");
  modalBody.innerHTML = `<div style="display: flex; flex-direction: column; margin-left: 10px;">
    <div style="display: flex; margin-right: 10px; padding: 5px; text-align: center;">
      <div style="margin: 3px 0; display: flex;font-size: 18px;">評価</div>
      <div style="margin: 3px 0; display: flex;font-size: 18px;margin-left:15px">口コミ</div>
    </div>
  </div>`;

  const reviewContainer = document.createElement("div");
  reviewContainer.style.overflowY = "auto";
  reviewContainer.style.maxHeight = "250px"; // 適切な高さに調整してください

  data.reviews.forEach(function (review) {
    let reviewItem = document.createElement("div");
    reviewItem.innerHTML = `<div style="display: flex; margin-left: 10px;">
      <p style="margin-top:10px; margin-bottom:10px; margin:3px 0; width:50px; text-align:center; border:1px solid;">${review[3]}</p>
      <p style="font-size: 10px; overflow-y: scroll; margin:3px 0; width: 550px; height: 30px; border:1px solid;">　${review[4]}</p>
      <button style="background-color: red; color:white; margin:3px 0; border:1px solid; height:30px; weight:30px;" class="delete-button" data-review-id="${review[0]}">削除</button>
    </div>`;
    reviewContainer.appendChild(reviewItem);
  });

  modalBody.appendChild(reviewContainer);

  // 削除ボタンがクリックされたときの処理を設定
  document.querySelectorAll(".delete-button").forEach((button) => {
    button.addEventListener("click", function () {
      const reviewId = this.getAttribute("data-review-id");
      // モーダル内の対象口コミを即座に削除
      document.querySelector(`[data-review-id="${reviewId}"]`).remove();
      // サーバー側の削除処理を行う
      deleteReview(reviewId);
    });
  });

  document.querySelector(".layer.review-modal").classList.add("is-open");
}

function deleteReview(reviewId) {
  fetch(`/delete_review1/${reviewId}`, { method: "GET" })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // 削除成功時の処理（UIから該当の口コミを削除するなど）
      console.log("Review deleted successfully");
      // 以下に必要なUI更新などの処理を追加
    })
    .catch((error) => console.error("Error deleting review:", error));
}

function closeReviewModal() {
  document.querySelector(".layer.review-modal").classList.remove("is-open");
}
//ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
